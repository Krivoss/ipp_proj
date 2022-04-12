import os.path
import sys
import re

# TODO dont let help with anything else
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

def error_exit_on_instruction(order, opcode, error_code, error_message, *args):
    print(f"Error: instruction n.{order} {opcode}: {error_message}", end='', file=sys.stderr)
    for a in args:
        a = value_for_print(a)
        print('', a, end='', file=sys.stderr)
    print(file=sys.stderr)
    exit(error_code)

def error_exit_xml_format():
    print("Error: invalid XML format", file=sys.stderr)
    exit(31)

def args_process():
    args = prog_arguments()
    args.process_args()
    return args

def value_for_print(value):
    if type(value) == bool:
        if value == True:
            return 'true'
        else:
            return 'false'
    else:
        return value

def convert_to_char(match_obj):
    if match_obj.group() is not None:
        num = int(match_obj.group()[1:])
        return chr(num)

def str_escape(string : str):
    return re.sub(r'\\\d{3}', convert_to_char, string)

def get_symb_value(instr, scopes, symb):
    if symb.get_type() == 'var':
        val = scopes.get_var(instr, symb.get_value(instr)).get_value(instr)
    else:
        val = symb.get_value(instr)
    return val

def get_symb_type(instr, scopes, symb):
    if symb.get_type() == 'var':
        get_symb_value(instr, scopes, symb)
        val_type = scopes.get_var(instr, symb.get_value(instr)).get_type()
    else:
        val_type = symb.get_type()
    return val_type

def get_symb_type_no_err(instr, scopes, symb):
    if symb.get_type() == 'var':
        val_type = scopes.get_var(instr, symb.get_value(instr)).get_type()
    else:
        val_type = symb.get_type()
    return val_type
