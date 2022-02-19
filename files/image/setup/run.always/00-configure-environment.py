#!/usr/bin/python3

import importlib.util
import os
import sys
import subprocess

# Import utils
spec = importlib.util.spec_from_file_location(
    "module.name", f"{os.environ.get('IMAGE_BASE_DIR')}{os.sep}utils.py"
)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

sys.stdout.write(
    f"Saving environment to {utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env;"
)

# Write all env variable to a file and check the current and the historic env state.
# Match the both states and create the diffs of both states
if os.path.exists(f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env"):
    os.chmod(utils.get_env_variable("IMAGE_CONFIG_DIR"), 0o775)

    if os.path.exists(f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env2"):
        os.remove(f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env2")

    cmd = (
        f"/usr/bin/env | sed -e 's/=/=\"/' -e 's/$/\"/' | /usr/bin/sort | "
        f"/bin/egrep -v 'HOSTNAME|SHLVL|HOME|TERM|PWD' > {utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env2"
    )
    rs = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if rs.returncode is not None:
        sys.stderr.write(f"Script error: {rs.returncode}")
        sys.exit(1)

    file_1 = f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env"
    file_2 = f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env2"

    cmd = f"diff {file_1} {file_1}"
    rs = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if rs.returncode is not None:
        sys.stderr.write("Old and new env file didn't include the sames values;")

        sys.exit(1)
    else:
        cmd = (
            "/usr/bin/env | sed -e 's/=/=\"/' -e 's/$/\"/' | /usr/bin/sort | /bin/egrep -v "
            "'HOSTNAME|SHLVL|HOME|TERM|PWD' > {utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env"
        )
        rs = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        if rs.returncode is not None:
            sys.stderr.write(f"Script error: {rs.returncode}")
            sys.exit(1)

        os.remove(f"{utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env2")
        os.chmod(utils.get_env_variable("IMAGE_CONFIG_DIR"), 0o555)
else:
    cmd = (
        f"/usr/bin/env | sed -e 's/=/=\"/' -e 's/$/\"/' | /usr/bin/sort | "
        f"/bin/egrep -v 'HOSTNAME|SHLVL|HOME|TERM|PWD' > {utils.get_env_variable('IMAGE_CONFIG_DIR')}{os.sep}env"
    )
    rs = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if rs.returncode is not None:
        sys.stderr.write(f"Script error: {rs.returncode}")
        sys.exit(1)
