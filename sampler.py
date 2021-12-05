# python -m pip install --upgrade pymupdf

import os
import re
import shutil
import random
import fitz

CUR_DIR = os.path.dirname(__file__)
OUT_DIR = "SAMPLE"

WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

EXTS = ["rtf", "pdf"]

num_constructed_weeks = 12

def main():    
    sort()
    sample()

def sort():
    """Finds and sorts all rtf or pdf files in the working directory by weekday"""
    files = []

    dir_listing = os.scandir()
    for i in dir_listing:
        if i.is_file() and i.name.split(".")[-1].lower() in EXTS:
            files.append(i.name)
    dir_listing.close()

    if len(files) > 0:
        for e, i in enumerate(files):
            ext = i.split(".")[-1].lower()
            if ext == "rtf":
                with open(i, "r") as f:
                    text = f.read()
            elif ext == "pdf":
                f = fitz.open(i)
                for page in f:
                    text = page.get_text("text")
                    break # we only need the first page to extract the weekday
                f.close()
            
            # Extracts weekday from the following string format: "February 4, 2021 Thursday 7:45 AM GMT" (as found in Lexis docs)
            from dateutil import parser
            # try:
            #   date, weekday = re.search(r"([a-zA-Z]+\s\d{1,2}),\s\d{4}\s([a-zA-Z]+)", text).groups() # \s\d{1,2}:\d{2}\s[A-Z]{2}\s[A-Z]{3}
            # except AttributeError:
            try:
              date = re.search(r"([a-zA-Z]+\s\d{1,2}),\s\d{4}", text).group(0)
              weekday = parser.parse(date).strftime("%A")
              # print(date, weekday)
            except AttributeError:
              date = re.search(r"\d{1,2}\s[a-zA-Z]+\s\d{4}", text).group(0)
              weekday = parser.parse(date).strftime("%A")
              # print(date, weekday)
            
            # Sorting docs by weekday
            print(f"Sorting {e+1}/{len(files)}") # simple progress bar
            from_ = os.path.join(CUR_DIR, i)
            to = os.path.join(CUR_DIR, f"{weekday}/{date}/{i}")
            os.makedirs(os.path.dirname(to), exist_ok=True)
            shutil.move(from_, to) # moves the doc to its respective weekday/date folder
    else:
        print("No files to sort!")
        exit()

def sample():
    """Performs constructed WEEK sampling from sorted documents with n-weeks"""
    print("Sampling...")

    for day in WEEK:
        hat = []

        try:
            dir_listing = os.scandir(os.path.join(CUR_DIR, day))
            for i in dir_listing:
                if i.is_dir():
                    hat.append(i.name)
            dir_listing.close()
        except FileNotFoundError:
            print(f"Warning: no documents found for {day}")
            break

        # Checks whether the number of docs is enough for sampling n-weeks, otherwise uses the whole population, or errors out if no docs are found
        if len(hat) > num_constructed_weeks:
            sample = random.sample(hat, num_constructed_weeks)
            for n in sample:
                dir_listing = os.scandir(os.path.join(CUR_DIR, day, n))
                for i in dir_listing:
                    if i.is_file():
                        from_ = os.path.join(CUR_DIR, day, n, i.name)
                        to = os.path.join(CUR_DIR, OUT_DIR, i.name)
                        os.makedirs(os.path.dirname(to), exist_ok=True)
                        shutil.move(from_, to) # Moves sampled docs to the output directory
                dir_listing.close()
        elif 0 < len(hat) <= num_constructed_weeks:
            print(f"Warning: using whole day's population for {day}")
            for N in hat:
                dir_listing = os.scandir(os.path.join(CUR_DIR, day, N))
                for i in dir_listing:
                    if i.is_file():
                        from_ = os.path.join(CUR_DIR, day, N, i.name)
                        to = os.path.join(CUR_DIR, OUT_DIR, i.name)
                        os.makedirs(os.path.dirname(to), exist_ok=True)
                        shutil.move(from_, to) # Moves sampled docs to the output directory
                dir_listing.close()
        else: # if 0 documents
            print(f"Error: nothing to sample!")
            exit()

    print("Done!")

if __name__ == "__main__":
    main()