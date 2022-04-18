'''
    File name: interpret_functions.py
    Author: Jakub Krivanek (xkriva30), FIT
    Date: April 2022 (academic year 2021/2022)
    Python Version: 3.8
    Brief: File for argument parsing and some helper functions
'''

import os.path
import sys
import re

class program_arguments:
    """
    A class to encapsulate program arguments
    """
    def __init__(self):
        self.will_print_help = False
        self.has_source_file = False
        self.has_input_file = False
        self.source_file = '-'
        self.input_file = '-'     

    def process_args(self):
        """
        Method for processing arguments

        If arguments are valid the arguments will be executed or the data will be stored in the object
        """
        for arg in sys.argv:
            # -h, --help
            if arg == '-h' or arg == '--help':
                for a in sys.argv[1:]:
                    if a != '-h' and a != '--help':
                        print("Error: cannot combine -h or --help with other arguments", file=sys.stderr)
                        exit(10)
                self.will_print_help = True
            # --source=SOURCE
            source = re.search(r"(?<=--source=)\S+", arg)
            if source:
                source = source.group()
                file_validity(source, 'source') 
                self.has_source_file = True
                self.source_file = source
            # --input=INPUT
            input = re.search(r"(?<=--input=)\S+", arg)
            if input:
                input = input.group()
                file_validity(input, 'input')                   
                self.has_input_file = True
                self.input_file = input

        if self.will_print_help:
            print_help()
            exit(0)

        missing_both_files = (not self.has_input_file) and (not self.has_source_file)
        if missing_both_files:
            print_help()
            print("\nError: one of the arguments --source --input is required", file=sys.stderr)
            exit(10)

    def get_source_file(self):
        """
        Returns open file or stdin
        """
        if self.has_source_file:
            file = open(self.source_file)
        else:
            file = sys.stdin
        return file

    def get_input_file(self):
        """
        Returns open file or stdin
        """
        if self.has_input_file:
            file = open(self.input_file)
        else:
            file = sys.stdin
        return file

def file_validity(file_str, type):
    """
    Exits if file is not valid
    """
    path = os.path.normpath(file_str)
    if not os.path.isfile(path):
        print(f"Error: --{type} file \"{file_str}\" does not exist", file=sys.stderr)
        exit(11)

def print_help():
    """
    Prints help message
    """
    print("usage: interpret.py [-h] (--source SOURCE | --input INPUT)\n\n"
            "optional arguments:\n"
            "  -h, --help       show this help message and exit\n"
            "  --source SOURCE  source file with XML of source code\n"
            "  --input INPUT    file with input for interpret", file=sys.stderr)

def error_exit_xml_format():
    print("Error: invalid XML format", file=sys.stderr)
    exit(31)

def args_process():
    """
    Processes the program arguments

    Returns program_arguments object
    """
    args = program_arguments()
    args.process_args()
    return args

def value_for_print(value):
    """
    Returns value for printing
    """
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
    """
    Returns string with escape sequences changed to characters
    """
    return re.sub(r'\\\d{3}', convert_to_char, string)

def get_symb_value(instr, scopes, symb):
    """
    Returns value of symb
    """
    if symb.get_type() == 'var':
        val = scopes.get_var(instr, symb.get_value(instr)).get_value(instr)
    else:
        val = symb.get_value(instr)
    return val

def get_symb_type(instr, scopes, symb):
    """
    Returns type of symb
    """
    if symb.get_type() == 'var':
        get_symb_value(instr, scopes, symb)
        val_type = scopes.get_var(instr, symb.get_value(instr)).get_type()
    else:
        val_type = symb.get_type()
    return val_type

def get_symb_type_no_err(instr, scopes, symb):
    """
    For instruction TYPE

    Returns type of symb    
    """
    if symb.get_type() == 'var':
        val_type = scopes.get_var(instr, symb.get_value(instr)).get_type()
    else:
        val_type = symb.get_type()
    return val_type
