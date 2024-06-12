import csv
from tqdm import tqdm
import os
import sys
from util import get_file_list, print_info, get_file_size_mb, rm_file
from config import Config
import re

config = Config()

os.environ['ROWS_COUNT'] = str(0)

def increment_rows_count():
    os.environ['ROWS_COUNT'] = str(int(os.environ['ROWS_COUNT']) + 1)

def filter_files_by_commit_count(files):
    finally_files = []
    for file in tqdm(files):
        with open(file, newline='', errors="ignore") as csvfile:
            reader = csv.reader(csvfile)
            i = 0
            for _ in reader:
                if i < config.MIN_COMMIT_COUNT:
                    i += 1
                    continue
                finally_files.append(file)
                break
            
    return finally_files

def isCorrect(row):
    if len(row) != 2:
        print(f'Wrong row length: {len(row)}')
        return False
    
    diff = row[0]
    message = row[1]


    bregexp_for_merge = r'\b(merge(d|s|ing|es|able|ment)?|pull(ed|s|ing)?|push(ed|es|ing)?)\b|[^\x00-\x7F]'

    if len(diff) > config.MAX_DIFF_LENGTH:
        print('Max diff length exceeded')
        return False

    if len(message) < config.MIN_COMMIT_MESSAGE_LENGTH and len(row[1]) > config.MAX_COMMIT_MESSAGE_LENGTH:
        print(f'Max commit message length exceeded. length: {len(message)}')
        return False
    
    if re.search(bregexp_for_merge, message, flags=re.IGNORECASE) is not None:
        print(f'Merge commit found: {message}')
        return False
    
    return True

def write_to_merged_file(file_path):
    with open(file_path, newline='', errors="ignore") as icsvfile, open(config.CLEANED_AND_MERGED_FILE_PATH, mode='a', newline='', errors="ignore") as ocsvfile:
        writer = csv.writer(ocsvfile)
        reader = csv.reader(icsvfile)
        for row in reader:
            if isCorrect(row):
                increment_rows_count()
                writer.writerow(row)
    return

def start():
    files = get_file_list(config.DIRTY_DATA_PATH)

    print_info('Filtering files by commit count')

    filtered_files = filter_files_by_commit_count(files)
    
    print_info([f'Romoved files count: { len(files) - len(filtered_files) }', f'Files remained count: { len(filtered_files) }'])
    
    for file in tqdm(filtered_files):
            write_to_merged_file(file)
            rm_file(file)
            
    print_info([f'Written rows count: { os.environ['ROWS_COUNT'] }', f'Clined file size: { get_file_size_mb(config.CLEANED_AND_MERGED_FILE_PATH) } MB'])

if __name__ == '__main__':
    maxInt = sys.maxsize

    while True:
        # decrease the maxInt value by factor 10 
        # as long as the OverflowError occurs.

        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/2)
    
    rm_file(config.CLEANED_AND_MERGED_FILE_PATH)
    start()