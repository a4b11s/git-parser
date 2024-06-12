import requests
import csv
from tqdm import tqdm
import re
import time
from util import Config
from yaml import load, dump, FullLoader
import multiprocessing as mp
import os

config = Config()

def parse_urls(res):
    urls = re.findall(r'},"html_url":"([^"]+)"', res)

    forrmated_urls = [(lambda x: [x + ".git"])(x) for x in urls]
    return forrmated_urls


def save_data(res):
    global start_time
    
    urls = parse_urls(res)
    csv_path = f"{config.URLS_PATH}{start_time}/{str(time.time())}.csv"

    with open(csv_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(urls)


def start():
    global start_time
    start_time = int(time.time()) 
    os.makedirs(f'{config.URLS_PATH}{start_time}', exist_ok=True)

    authHeader = {
        "Authorization": "Bearer " + "TOKEN"
    }

    poll = mp.Pool(int(config.MAX_WORKERS))
    
    response = requests.get("https://api.github.com/rate_limit", headers=authHeader)
    limit = int(response.json()["resources"]["core"]["remaining"])

    with open("db.yaml", mode="r") as db:
        data = load(db.read(), Loader=FullLoader)
        last_id = data["last_url_id"]

    for _ in tqdm(range(limit)):
        response = requests.get(
            "https://api.github.com/repositories",
            params={"since": last_id},
            headers=authHeader,
        )
        last_id = re.findall(r'{"id":(\d+),', response.text)[-1]

        with open("db.yaml", mode="w") as db:
            data["last_url_id"] = last_id
            db.write(dump(data, default_flow_style=False))
            
        poll.apply_async(save_data, (response.text,))

    poll.close()
    
if __name__ == "__main__":
    start()
