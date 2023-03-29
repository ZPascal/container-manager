#!/usr/bin/python3

import importlib.util
import os
import sys
import glob
import subprocess

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

sys.stdout.write(
    "Replacing environment variables (directory definitions) in logrotate configuration.;"
)

sed_script_start = "sed -i"

values: list = utils.extract_dir_env_vars()

# Collect all logrotate config files
logrotate_configs = glob.glob(
    f"{utils.get_env_variable('IMAGE_LOGGING_DIR')}{os.sep}logrotate-*.conf"
)
logrotate_configs.extend(
    sorted(
        glob.glob(
            f"{utils.get_env_variable('IMAGE_LOGGING_DIR')}{os.sep}logrotate.d{os.sep}logrotate-*.conf"
        )
    )
)

# Rename env variables to all native path entries inside all logrotate config files
for line in values:
    name = line.split("=")[0]
    name = "\\${%s}" % name
    value = line.split("=")[1].replace('"', "").replace("\n", "")

    sed_script = f'{sed_script_start} -e "s|{name}|{value}|g"'

    logging_dir = utils.get_env_variable("IMAGE_LOGGING_DIR")
    os.chmod(logging_dir, 0o755)
    os.chmod(f"{logging_dir}{os.sep}logrotate.d", 0o755)

    for file in logrotate_configs:
        sed_script_local = f"{sed_script} {file}"
        result = subprocess.run(
            sed_script_local,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        if result.returncode != 0:
            sys.stderr.write(
                f"Error, please check the script: {sed_script_local}, ERR: {result.stdout};"
            )
            sys.exit(1)

# Set logrotate crontab entries
sys.stdout.write("Creating crontab entry for logrotate;")
with open(f"{utils.get_env_variable('IMAGE_CRON_DIR')}{os.sep}kubernetes", "a") as f:
    f.write(
        f"{utils.get_env_variable('IMAGE_LOGROTATE_CRON')} "
        f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env; /usr/sbin/logrotate -f -s /tmp/logrotate.status "
        f"{utils.get_env_variable('IMAGE_LOGGING_DIR')}{os.sep}logrotate-global.conf\n"
    )
