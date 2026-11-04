import subprocess
import sys, os
import platform
import math
import signal
from shutil import which

GetParams = GetParams # type: ignore
SetVar = SetVar # type: ignore
PrintException = PrintException # type: ignore

base_path = tmp_global_obj["basepath"] # type: ignore
cur_path = base_path + 'modules' + os.sep + 'ScriptsAdvanced' + os.sep + 'libs' + os.sep


if cur_path not in sys.path:
    sys.path.append(cur_path)

module = GetParams("module")

try:

    if module == "python":
        try:
            file = GetParams("file")
            result_studio = GetParams("result")
            args = eval(GetParams("arguments")) if GetParams("arguments") else []

            if args and not isinstance(args, list):
                raise Exception("Arguments must be a list")

            if not file.endswith(".py"):
                raise Exception("Only Python files are supported.")

            python_exec = "python"
            if platform.system() == "Darwin":
                python_exec = "python3" if which("python3") else "python"
            elif platform.system() == "Linux":
                python_exec = "python3" if which("python3") else "python"

            parameters = [python_exec, file]
            parameters.extend(args)

            result = subprocess.run(parameters, check=False, capture_output=True, text=True)
            
            if "CommandNotFoundException" in result.stderr:
                raise Exception("Python not found locally, please install it and add to the path following this link:\nhttps://realpython.com/add-python-to-path/")

            if result.returncode != 0:
                raise Exception(result.stderr)

            SetVar(result_studio, result.stdout)

        except Exception as e:
            PrintException()
            raise e
        
    if module == "node":
        try:
            file = GetParams("file")
            result_studio = GetParams("result")
            args = eval(GetParams("arguments")) if GetParams("arguments") else []
            if args and not isinstance(args, list):
                raise Exception("Arguments must be a list")

            if not file.endswith(".js"):
                raise Exception("No Node files are not supported for Node interpreter")

            parameters = ['node', file]
            parameters.extend(args)

            result = subprocess.run(parameters, check=False, capture_output=True, text=True)

            if "CommandNotFoundException" in result.stderr:
                raise Exception("Node not found locally, please install it following this link:\nhttps://nodejs.org/")

            if result.returncode != 0:
                raise Exception(result.stderr)
            
            SetVar(result_studio, result.stdout)

        except Exception as e:
            PrintException()
            raise e
        
    if module == "cli":
        instructions = GetParams("instructions").split('\n')
        result_studio = GetParams("result")
        output = []
        errors = []

        try:
            timeout_value = GetParams("timeout")
            try:
                timeout = float(timeout_value) if timeout_value is not None and str(timeout_value).strip() else 60.0
            except (TypeError, ValueError):
                raise ValueError("Command timeout must be a positive number of seconds.")
            if not math.isfinite(timeout) or timeout <= 0:
                raise ValueError("Command timeout must be a positive number of seconds.")

            for instruction in instructions:

                # Isolate the shell so its child commands can also be stopped.
                process_options = {}
                if os.name == "nt":
                    process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
                else:
                    process_options["start_new_session"] = True
                with subprocess.Popen(instruction, shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, **process_options) as process:
                    try:
                        stdout, stderr = process.communicate(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        if os.name == "nt":
                            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                           check=False, timeout=10)
                        else:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        process.kill()
                        stdout, stderr = process.communicate()
                        output.append(stdout)
                        SetVar(result_studio, [item.strip() for item in output])
                        raise TimeoutError(
                            "Command exceeded the timeout of {:g} seconds: {}".format(timeout, instruction))

                if process.returncode != 0:
                    errors.append(stderr.strip())
                
                output.append(stdout)
            if errors:
                raise Exception('\n'.join(errors))

            output = [item.strip() for item in output]

            SetVar(result_studio, output)

        except Exception as e:
            PrintException()
            raise e

except Exception as e:
    PrintException()
    raise e