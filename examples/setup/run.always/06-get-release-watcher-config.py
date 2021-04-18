#!/usr/bin/python3

import importlib.util
import os
import subprocess
import sys
import shutil

spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

artifact_name: str = "release-watcher"
token: str = utils.get_env_variable("RELEASE_WATCHER_GIT_TOKEN")
repo_url: str = f"https://{token}@git.theiotstudio.com/The_IOT_Studio/release-watcher"
repo_branch: str = "deployment"
path_repo: str = f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}{artifact_name}"
file_path: str = f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}releases.yml"

try:
    if os.path.exists(file_path):
        sys.stdout.write("Remove old config file if it exists;")
        os.remove(file_path)
except Exception as e:
    sys.stdout.write(f"Can not remove the config file. Check the error: {e};")
    sys.exit(1)

try:
    sys.stdout.write("Git clone the repository;")
    command = [
        "git",
        "clone",
        repo_url,
        "--single-branch",
        f"--branch={repo_branch}",
        path_repo,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        sys.stdout.write("Git clone didn't work;")
        sys.exit(1)
except ValueError as e:
    sys.stdout.write(f"Can not clone the repository. Check the error: {e};")
    sys.exit(1)

try:
    sys.stdout.write("Move file;")
    shutil.move(f"{path_repo}{os.sep}releases.yml", file_path)
except Exception as e:
    sys.stdout.write(f"Can not move the file. Check the error: {e};")
    sys.exit(1)

try:
    sys.stdout.write("Remove repo and git folder;")
    if os.path.exists(path_repo):
        shutil.rmtree(path_repo, ignore_errors=True)
        shutil.rmtree(
            f"{utils.get_env_variable('STORAGE_CONF_DIR')}{os.sep}.git",
            ignore_errors=True,
        )
except Exception as e:
    sys.stdout.write(f"Can not remove the files and folders. Check the error: {e};")
    sys.exit(1)
