#!/usr/bin/python3

import importlib.util
import argparse
import datetime
import glob
import os
import re


# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Import restore
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_RESTORE_DIR')}{os.sep}restore.py"
)
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)

image_setup_run_once_marker_file = (
    f"{utils.get_env_variable('STORAGE_BASE_DIR')}/.run-once.completed"
)
image_base_dir = utils.get_env_variable("IMAGE_BASE_DIR")
image_supervisor_config = f"{image_base_dir}/supervisor/global.conf"

# Executing run always scripts
utils.write_log("info", os.path.basename(__file__), "Executing RUN ALWAYS setup ...")

run_always_scripts = sorted(
    glob.glob(f"{utils.get_env_variable('IMAGE_SETUP_RUNALWAYS_DIR')}{os.sep}*.py")
)
utils.execute_scripts(run_always_scripts)

utils.write_log("info", os.path.basename(__file__), "[done]")

# Make folder non-writable
utils.write_log(
    "info", os.path.basename(__file__), f"Marking {image_base_dir} non-writable"
)

os.chmod(image_base_dir, 0o555)

dirs_list = list()
for dirs, _, _ in os.walk(utils.get_env_variable("IMAGE_BASE_DIR")):
    dirs_list.append(dirs)

# Make secrets non-writable
r = re.compile(f"{utils.get_env_variable('IMAGE_SECRETS_DIR')}{os.sep}*")
dirs_remove_list = list(filter(r.match, dirs_list))
dirs_list = [dirs for dirs in dirs_list if dirs not in dirs_remove_list]

for dirs in dirs_list:
    utils.set_permissions_recursive(dirs, 0o555)

# Run setup scripts only on first start. Check if corresponding file exists
if os.path.isfile(image_setup_run_once_marker_file) is False:
    utils.write_log("info", os.path.basename(__file__), "Executing RUN ONCE setup ...")

    run_once_scripts = sorted(
        glob.glob(f"{utils.get_env_variable('IMAGE_SETUP_RUNONCE_DIR')}{os.sep}*.py")
    )
    utils.execute_scripts(run_once_scripts)

    f = open(image_setup_run_once_marker_file, "w")
    f.write(datetime.datetime.now().astimezone().strftime("%a %d. %b %H:%M:%S %Z %Y"))
    f.close()

    utils.write_log("info", os.path.basename(__file__), "[done]")

    utils.write_log(
        "info", os.path.basename(__file__), "Looking for backups to restore"
    )

    backup_file = ""

    # Check if backup exists and maybe restore the backups on first image start
    if (
        len(
            glob.glob(
                f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}{os.sep}backup-*.tar.gz"
            )
        )
        != 0
    ):
        backup_file = glob.glob(
            f"{utils.get_env_variable('STORAGE_BACKUP_DIR')}{os.sep}backup-*.tar.gz"
        )[0]

    if backup_file != "":
        utils.write_log(
            "info",
            os.path.basename(__file__),
            f"Backup found. Data will be restored from {backup_file}",
        )
        restore.restore_data(backup_file)
    else:
        utils.write_log("info", os.path.basename(__file__), "No backup found")

# If a variable is not passed, the supervisord process runs. If a variable is passed, the command is executed.
parser = argparse.ArgumentParser()
parser.add_argument("-variable", type=str, default="")
args = parser.parse_args()

if args.variable == "":
    utils.write_log(
        "info",
        os.path.basename(__file__),
        f"/usr/bin/supervisord -c {image_supervisor_config}",
    )
    utils.write_log(
        "info", os.path.basename(__file__), "Starting container (supervisord) ..."
    )
    os.system(f"/usr/bin/supervisord -c {image_supervisor_config}")
else:
    utils.write_log(
        "info", os.path.basename(__file__), f"Executing command {args.variable}"
    )
    os.system(f"{args.variable}")
