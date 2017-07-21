from __future__ import print_function

from subprocess import Popen, PIPE
import os
import base64
import pip
import traceback

print('Loading function')


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
    fil_path = "/tmp/"
    fil = open(fil_path+"main.py", "wb")
    data = event["code"]
    fil.write(data)
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
        pip.main(["install", '-t', fil_path, "pip"])
        pip.main(["install", '-t', fil_path, "setuptools"])
        pip.main(["install", '-t', fil_path, "wheel"])
        for package in packages:
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
    p = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            )
    output, error = p.communicate(input=input_string)
    if p.returncode != 0:
        ret["message"] = base64.b64encode(error)
    else:
        ret["message"] = base64.b64encode(output)
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


def _remove_envs():
    required_envs = [
        'AWS_LAMBDA_LOG_STREAM_NAME',
        'AWS_LAMBDA_LOG_GROUP_NAME',
        'AWS_LAMBDA_FUNCTION_NAME',
        'AWS_LAMBDA_FUNCTION_MEMORY_SIZE',
        'AWS_LAMBDA_FUNCTION_VERSION',
    ]
    try:
        for key, value in os.environ.items():
            if key not in required_envs:
                del os.environ[key]
    except:
        print(traceback.print_exc())
