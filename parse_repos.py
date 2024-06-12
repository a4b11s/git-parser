import git
import csv
import hashlib
from tqdm import tqdm
import multiprocessing as mp
from util import clear_dir, get_file_list, rm_file
from config import Config

config = Config()

skip = 0

is_exit = False


def extract_info_from_repo(repository):
    with repository:
        iter = repository.iter_commits()
        total = repository.git.rev_list("--count", "HEAD")
    return iter, total


def repo_to_csv(iter, total, repository, out_csv_path):
    if int(total) < int(config.MIN_COMMIT_COUNT):
        return

    for commit in tqdm(
        iter, total=int(total), leave=False, desc="commits", unit="commit"
    ):
        perents = commit.parents
        if len(perents) == 0:
            continue

        diff = repr(
            repository.git.diff(
                commit.hexsha,
                perents[0].hexsha,
                ignore_blank_lines=True,
                ignore_space_at_eol=True,
            )
        )

        with open(out_csv_path, mode="a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([diff, commit.message])


def clone_repo(url, path_to_git):
    repository = git.Repo.clone_from(url, path_to_git)
    return repository


def worker(url):
    url = url.replace("https://", "https://user:password@")
    url_sha = hashlib.sha256(bytes(url, "UTF-8")).hexdigest()
    path_to_git = config.GITS_PATH + url_sha
    out_csv_path = f"{config.DIRTY_DATA_PATH}{url_sha}.csv"

    try:
        repository = clone_repo(url, path_to_git)
    except Exception as e:
        clear_dir(path_to_git)
        return

    try:
        iter, total = extract_info_from_repo(repository)
    except Exception as e:
        clear_dir(path_to_git)
        return

    try:
        repo_to_csv(iter, total, repository, out_csv_path)
    except Exception as e:
        print(e)
    finally:
        clear_dir(path_to_git)


def parse_file(csv_path):
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        reader_list = list(reader)
        args = [row[0] for row in reader_list[skip:]]
        with mp.Pool(int(config.MAX_WORKERS)) as pool:
            pool.map(worker, args)

    rm_file(csv_path)


def parse_dir(dir_path):
    files = get_file_list(dir_path + "/")

    procs = []

    for file in tqdm(files, desc="Files", unit="file", total=len(files), leave=False):

        while len(procs) > 10:
            proc = procs.pop()
            proc.join()

        for proc in procs:
            if proc.is_alive():
                pass
            else:
                procs.remove(proc)

        proc = mp.Process(target=parse_file, args=(file,))
        proc.start()
        procs.append(proc)


def start():
    dirs = get_file_list(config.URLS_PATH)

    for dir in tqdm(dirs, desc="Dirs", unit="dir"):
        parse_dir(dir)
        clear_dir(dir)


if __name__ == "__main__":
    start()
