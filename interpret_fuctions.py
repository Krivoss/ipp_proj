import os.path
import sys

from numpy import var

import interpret_classes as i_class

def file_validity(file_str, type):
    path = os.path.normpath(file_str)
    if not os.path.isfile(path):
        print(f"Error: --{type} file \"{file_str}\" does not exist", file=sys.stderr)
        exit(11)

def print_help():
        print("usage: interpret.py [-h] (--source SOURCE | --input INPUT)\n\n"
              "optional arguments:\n"
              "  -h, --help       show this help message and exit\n"
              "  --source SOURCE  Source file with XML of source code\n"
              "  --input INPUT    File with input for interpret", file=sys.stderr)  

def error_exit_on_instruction(order, instruction, error_message, error_code):
    print(f"Error: instruction n.{order} {instruction}: {error_message}", file=sys.stderr)
    exit(error_code)

def get_const_val(const):
    if const.startswith("int@"):
        return const[4:]
    elif const.startswith("string@"):
        return const[6:]

def args_process():
    args = i_class.prog_arguments()
    args.process_args()
    return args