import subprocess
import sys, os

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

            parameters = ['python', file]
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
            for instruction in instructions:

                result = subprocess.run(instruction, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    errors.append(result.stderr.strip())
                
                output.append(result.stdout)
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