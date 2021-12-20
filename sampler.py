#! python3

# python -m pip install --upgrade pymupdf python-docx

import os, re, shutil, random
import fitz, docx

CUR_DIR = os.path.dirname(__file__)
OUT_DIR = "SAMPLE"
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
EXTS = ["rtf", "pdf", "docx"]

num_constructed_weeks = 6

def main():
    sort()
    reduce(2)
    sample()

def sort():
    """Finds and sorts all rtf or pdf files in the working directory by weekday and date"""
    files = []
    dir_listing = os.scandir()
    for i in dir_listing:
        if i.is_file() and i.name.split(".")[-1].lower() in EXTS and "doclist" not in i.name.lower():
            files.append(i.name)
    dir_listing.close()

    if len(files) > 0:
        from tqdm import tqdm
        pbar = tqdm(files, bar_format="{l_bar}{bar}", ncols=50)
        for i in pbar:
            pbar.set_description(f"Sorting {len(files)}")
            ext = i.split(".")[-1].lower()
            if ext == "rtf":
                with open(i, "r") as f:
                    text = f.read()
            elif ext == "pdf":
                f = fitz.open(i)
                for page in f:
                    text = page.get_text("text")
                    break # we only need the first page
                f.close()
            elif ext == "docx":
                document = docx.Document(i)
                text = "\n".join([ paragraph.text for paragraph in document.paragraphs ])
            
            # Extracts and parses the date
            from dateutil import parser
            try:
              date = re.search(r"([a-zA-Z]+\s\d{1,2}),\s\d{4}", text).group(0)
              weekday = parser.parse(date).strftime("%A")
            except AttributeError:
              date = re.search(r"\d{1,2}\s[a-zA-Z]+\s\d{4}", text).group(0)
              weekday = parser.parse(date).strftime("%A")
            
            # Sorting docs by weekday
            # print(f"Sorting {e+1}/{len(files)}") # simple progress bar
            from_ = os.path.join(CUR_DIR, i)
            to = os.path.join(CUR_DIR, weekday, date, i)
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
        else: # if no documents found
            print(f"Error: nothing to sample!")
            exit()

    print("Done!")

def reduce(by):
    """Reduces the population by x before sampling"""
    print("Reducing...")

    # hat = []
    # try:
    #     dir_listing = os.scandir(os.path.join(CUR_DIR, OUT_DIR))
    #     for i in dir_listing:
    #         if i.is_file():
    #             hat.append(i.name)
    #     dir_listing.close()
    # except FileNotFoundError:
    #     print(f"Warning: no documents found! Exiting.")
    #     exit()
    # reduced_sample = random.sample(hat, int(len(hat)/by))
    # for i in reduced_sample:
    #     from_ = os.path.join(CUR_DIR, OUT_DIR, i)
    #     to = os.path.join(CUR_DIR, OUT_DIR, "DISCARDED", i)
    #     os.makedirs(os.path.dirname(to), exist_ok=True)
    #     shutil.move(from_, to) # Moves sampled docs to the output directory

    for day in WEEK:
        try:
            with os.scandir(os.path.join(CUR_DIR, day)) as dir_listing:
                for i in dir_listing:
                    if i.is_dir():
                        hat = []
                        with os.scandir(i.path) as subdir_listing:
                            for j in subdir_listing:
                                if j.is_file():
                                    hat.append(j.name)
                        if len(hat) > 1:
                            reduced_sample = random.sample(hat, round(len(hat)/by))
                            for file in reduced_sample:
                                from_ = os.path.join(CUR_DIR, day, i, file)
                                to = os.path.join(CUR_DIR, day, i, "DISCARDED", file)
                                os.makedirs(os.path.dirname(to), exist_ok=True)
                                shutil.move(from_, to) # Moves sampled docs to the output directory
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    main()