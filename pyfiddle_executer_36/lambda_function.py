from __future__ import print_function

from subprocess import Popen, PIPE
import os
import base64
import pip
import traceback

print('Loading function')

# IGNORE_PACKAGES = ["numpy", "scipy", "pandas"]
# TODO: Implement Packages for 3.6, its working for 2.7
IGNORE_PACKAGES = []


def lambda_handler(event, context):
    print(event)
    message = execute(event)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': message,
    }


def execute(event):
    remove_dirs = Popen("rm -rf /tmp/*", shell=True)
    remove_dirs.communicate()
    data = event["code"]
    fil_path = "/tmp/"
    fil = open(fil_path+"main.py", "wb")
    fil.write(bytes(data.encode("utf-8")))
    fil.close()
    args_string = event["commands"]
    if args_string != "":
        args = args_string.split(",")
    else:
        args = []
    arg_string = ''
    for arg in args:
        arg_string += " "+arg
    cmd = "sh -c 'cd /tmp/; python main.py"+arg_string+"'"
    packages_string = event["packages"]
    package_error_true = True
    if packages_string != "":
        packages = packages_string.split(",")[:5]
        for package in packages:
            can_install = True
            for item in IGNORE_PACKAGES:
                if item in package:
                    can_install = False
            if can_install:
                pip.main(["install", '-t', fil_path, package])
    input_string = ''
    for inp in event["inputs"].split(","):
        input_string += str(inp)+"\n"
    ret = {}
    if "fiddle_id" in event:
        if event["files_binary"]:
            file_create = _create_local_files_from_binary(
                event["files_binary"], fil_path)
            ret["files"] = file_create
    _remove_envs()
    _write_envs(event.get("envs", ""))
    p = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            )
    output, error = p.communicate(input=bytes(input_string.encode("utf-8")))
    if p.returncode != 0:
        ret["message"] = base64.b64encode(error).decode("utf-8")
    else:
        ret["message"] = base64.b64encode(output).decode("utf-8")
    ret["status"] = 0
    ret["packages"] = package_error_true
    return ret


def _create_local_files_from_binary(files, fil_path):
    try:
        for fil_name in files:
            fil = open(fil_path+fil_name, "wb")
            fil.write(base64.b64decode(files[fil_name]))
            fil.close()
    except:
        return False
    else:
        return True


def _write_envs(envs_string):
    envs = envs_string.split(',')
    if len(envs) % 2 == 0:
        env_keys = envs[0::2]
        env_values = envs[1::2]
        tuple_envs = zip(env_keys, env_values)
        for entry in tuple_envs:
            if not os.environ.get(entry[0], False):
                os.environ[entry[0]] = entry[1]


def _remove_envs():
    required_envs = [
        'AWS_LAMBDA_LOG_STREAM_NAME',
        'AWS_LAMBDA_LOG_GROUP_NAME',
        'AWS_LAMBDA_FUNCTION_NAME',
        'AWS_LAMBDA_FUNCTION_MEMORY_SIZE',
        'AWS_LAMBDA_FUNCTION_VERSION',
        'PATH',
        'LAMBDA_TASK_ROOT',
        'LD_LIBRARY_PATH'
    ]
    try:
        for key in list(os.environ.keys()):
            if key not in required_envs:
                del os.environ[key]
    except:
        print(traceback.print_exc())
