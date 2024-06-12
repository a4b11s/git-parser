import os
import shutil

def rm_file(path):
    if os.path.exists(path):
            os.remove(path)
            
def is_array(value):
    return isinstance(value, list)

def get_file_list(path):
    files = os.listdir(path)
    return [path+file for file in files]

def clear_dir(path):
    if os.path.exists(path):
            shutil.rmtree(path)
            
def print_info(message):
    terminal_simbols_count = os.get_terminal_size().columns
    separator = '*'
    separator_line = f"\n{separator*terminal_simbols_count}\n"
    
    if not is_array(message):
        message = [message]
    
    print(separator_line)
    
    for message_item in message:
        print(message_item.center(terminal_simbols_count))
        
    print(separator_line)
    
def get_file_size_mb(file_path):
    return round(os.path.getsize(file_path)/1/1024/1024)    

# TEMPORARY CONFIG, ADD LOAD IN FUTURE
class Config:
    def __init__(self):
        self.MIN_COMMIT_COUNT = 100
        self.MIN_COMMIT_MESSAGE_LENGTH = 10
        self.CLONE_TIMEOUT = 30
        self.MAX_WORKERS = 100
        
        self.DIRTY_DATA_PATH = 'output/'
        self.GITS_PATH = 'git/'
        self.URLS_PATH = 'url/'
        self.CLEANED_AND_MERGED_FILE_PATH = 'cleaned_output.csv'

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False