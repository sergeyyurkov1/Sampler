# python -m pip install --upgrade pymupdf

import os
import re
import shutil
import random
import fitz

CUR_DIR = os.path.dirname(__file__)
OUT_DIR = "SAMPLE"

week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

exts = ["rtf", "pdf"]

num_constructed_weeks = 2

def main():
    dirs = week + [OUT_DIR] # dirs to create
    for dir_ in dirs:
        if not os.path.isdir(dir_):
            os.mkdir(dir_)
        else:
            print("Sampling had already been done!")
            exit()
    
    sort()
    sample()

def sort():
    """Finds and sorts all rtf or pdf files in the working directory by weekday"""
    
    files = []

    dir_listing = os.scandir()
    for i in dir_listing:
        if i.is_file() and i.name.split(".")[-1].lower() in exts:
            files.append(i.name)
    dir_listing.close()

    if len(files) > 0:
        for e, i in enumerate(files):
            ext = i.name.split(".")[-1].lower()
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
            weekday = re.search(r"[a-zA-Z]+\s\d{1,2},\s\d{4}\s([a-zA-Z]+)\s\d{1,2}:\d{2}\s[A-Z]{2}\s[A-Z]{3}", text).group(1)
            
            # Sorting docs by weekday
            print(f"Sorting {e+1}/{len(files)}") # simple progress bar
            shutil.move(os.path.join(CUR_DIR, i), os.path.join(CUR_DIR, f"{weekday}/{i}")) # moves the doc to its respective weekday folder
    else:
        print("No files to sort!")
        exit()

def sample():
    """Performs constructed week sampling from sorted documents with n-weeks"""

    print("Sampling...")

    for day in week:
        hat = []

        dir_listing = os.scandir(os.path.join(CUR_DIR, day))
        for i in dir_listing:
            if i.is_file():
                hat.append(i.name)
        dir_listing.close()

        # Checks whether the number of docs on a given day is enough for sampling, otherwise uses the whole day's population or skips if no docs are found (len(hat) == 0)
        if len(hat) >= num_constructed_weeks:
            sample = random.sample(hat, num_constructed_weeks)
            for n in sample:
                shutil.move(os.path.join(CUR_DIR, f"{day}/{n}"), os.path.join(CUR_DIR, f"{OUT_DIR}/{n}")) # Moves sampled docs to the output directory
        elif 0 < len(hat) < num_constructed_weeks:
            print(f"Warning: using whole day's population for {day}")
            for N in hat:
                shutil.move(os.path.join(CUR_DIR, f"{day}/{N}"), os.path.join(CUR_DIR, f"{OUT_DIR}/{N}")) # Moves docs to the output directory
        else:
            print(f"Warning: no documents found for {day}")

    print("Done!")

if __name__ == "__main__":
    main()