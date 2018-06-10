from fuse import FUSE
import argparse
import yaml
from os.path import expanduser


from .operations import Filesystem
from .state_store import StateStore
from .cache import Cache
from .worker import Worker
from .paths import PathConverter
from .b2_api import FileAPI
from .ranker import Ranker
from .rank_store import RankStore
from .b2_file_info_store import FileInfoStore


def get_config():
    with open(expanduser("~/.config/zero/config.yml"), "r") as config:
        return yaml.load(config)


def parse_fuse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint", type=str, help="Mountpoint")
    parser.add_argument("cache_folder", type=str, help="Cache folder")
    return parser.parse_args()


def parse_worker_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cache_folder", type=str, help="Cache folder")
    return parser.parse_args()


def fuse_main():

    args = parse_fuse_args()
    config = get_config()

    converter = PathConverter(args.cache_folder)
    state_store = StateStore(config["sqliteFileLocation "])
    cache = Cache(converter, state_store)
    filesystem = Filesystem(cache)
    FUSE(
        filesystem, args.mountpoint, nothreads=True, foreground=True, debug=True
    )


def worker_main():

    args = parse_worker_args()
    config = get_config()

    file_info_store = FileInfoStore(config["sqliteFileLocation"])
    api = FileAPI(
        file_info_store=file_info_store,
        account_id=config["accountId"],
        application_key=config["applicationKey"],
        bucket_id=config["bucketId"],
    )

    converter = PathConverter(args.cache_folder)
    state_store = StateStore(config["sqliteFileLocation"])
    cache = Cache(converter, state_store)
    worker = Worker(cache, api)
    worker.run()


def decay_rank():
    config = get_config()

    rank_store = RankStore(config["sqliteFileLocation"])
    Ranker(rank_store).decay_rank()
