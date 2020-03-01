from argparse import ArgumentParser
import logging
import os
from pathlib import Path
import shutil

import pygit2
from tree_sitter import Language


REPO_PREFIX = 'https://github.com/tree-sitter/tree-sitter-'
TEMP_DOWNLOAD_PATH = "/tmp/tree-sitter-repos"

parser = ArgumentParser()
parser.add_argument("langs",
                    type=str,
                    nargs="+",
                    help="Give the name of languages for tree-sitter (php, python, go ...)")
parser.add_argument("-c",
                    "--copy-to-workspace",
                    action='store_true',
                    help="Shall we copy the created libs to the present dir?")
parser.add_argument("-l",
                    "--lib-name",
                    type=str,
                    default="my-languages.so",
                    required=False,
                    help="The name of the generated .so file")

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


repo_path = lambda x:  f"{TEMP_DOWNLOAD_PATH}/{x}"
lib_path = lambda x: os.getcwd() if x.copy_to_workspace else TEMP_DOWNLOAD_PATH


def clone_repo(lang_name):
    """
    Clone the necessary repo
    """
    if Path(repo_path(lang_name)).exists():
        shutil.rmtree(Path(repo_path(lang_name)))
    repo_url = f"{REPO_PREFIX}{lang_name}"
    try:
        r = pygit2.clone_repository(repo_url, repo_path(lang_name))
        return True if r else False
    except pygit2.GitError:
        return False


def make_tree_sitter_lib(args, lang_repo_list):
    """
    Create the library from the repos
    """
    lp = lib_path(args)
    lib_name = args.lib_name
    full_lib_creation_path = f"{lp}/{lib_name}"
    
    if Path(full_lib_creation_path).exists():
        os.remove(full_lib_creation_path)
    
    return Language.build_library(full_lib_creation_path, lang_repo_list)


def main():
    args = parser.parse_args()
    repo_arr = []
    for lang_name in args.langs:
        logging.info(f"Cloneing {lang_name} repo from tree-sitter collections")
        ret = clone_repo(lang_name)
        if ret:
            logging.info("Clone success")
            repo_arr.append(repo_path(lang_name))
        else:
            logging.error("Clone falied. Are you sure the language binding exists?")

    if repo_arr:
        logging.info(f"Creating the library {args.lib_name} at {lib_path(args)}")
        ret = make_tree_sitter_lib(args, repo_arr)
        if ret:
            logging.info("Finished creating library!")
    else:
        logging.info("No libraries could be created. Please try again")
