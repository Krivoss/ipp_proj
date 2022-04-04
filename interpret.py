import sys
import re
import os.path
import xml.etree.ElementTree as ET

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

class prog_arguments:
    def __init__(self):
        self._will_print_help = False
        self._has_source_file = False
        self._has_input_file = False
        self._source_file = '-'
        self._input_file = '-'     

    def process_args(self):
        for arg in sys.argv:
            # -h, --help
            if arg == '-h' or arg == '--help':
                self._will_print_help = True
            # --source=SOURCE
            source = re.search(r"(?<=--source=)\S+", arg)
            if source:
                source = source.group()
                file_validity(source, 'source') 
                self._has_source_file = True
                self._source_file = source
            # --input=INPUT
            input = re.search(r"(?<=--input=)\S+", arg)
            if input:
                input = input.group()
                file_validity(input, 'input')                   
                self._has_input_file = True
                self._input_file = input

        if self._will_print_help:
            print_help()
            exit(0)

        missing_both_files = (not self._has_input_file) and (not self._has_source_file)
        if missing_both_files:
            print_help()
            print("\nError: one of the arguments --source --input is required", file=sys.stderr)
            exit(10)

    def get_source_file(self):
        if self._has_source_file:
            file = open(self._source_file)
        else:
            file = sys.stdin
        return file

    def get_input_file(self):
        if self._has_input_file:
            file = open(self._input_file)
        else:
            file = sys.stdin
        return file

class argument:
    def __init__(self, type : str, content):
        self._type = type
        self._content = content


class instruction:
    def __init__(self, order : int, opcode : str):
        self._order = order
        self._opcode = opcode

class defvar(instruction):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, "DEFVAR")
        self._arg1 = arg1

class factory:
    @classmethod
    def get_instruction(cls, order : int, str_opcode : str,
                arg1 : argument = None, arg2 : argument = None, arg3 : argument = None):
        if str_opcode == 'DEFVAR':
            return defvar(order, arg1)
        # elif str_opcode == 'DEFVAR':

        # elif str_opcode == 'DEFVAR':
            
        # elif str_opcode == 'DEFVAR':
            
        # elif str_opcode == 'DEFVAR':
            
        # elif str_opcode == 'DEFVAR':
            
        # elif str_opcode == 'DEFVAR':
            

def args_process():
    args = prog_arguments()
    args.process_args()
    return args

def main():
    args = args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        # print(input_file.read())
        # print(source_file.read())
        myroot = ET.parse(source_file).getroot()

        arg1 = argument('string', 'Yo')
        defvar_instance = factory.get_instruction(1, 'DEFVAR', arg1)
        print("yo")

if __name__=="__main__":
    main()