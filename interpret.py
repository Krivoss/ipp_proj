import sys
import argparse
import re
import os.path

def file_validity(file_str, type):
    path = os.path.normpath(file_str)
    if not os.path.isfile(path):
        print(f"Error: --{type} file \"{file_str}\" does not exist", file=sys.stderr)
        exit(11)

class Arguments:
    def __init__(self):
        self._will_print_help = False
        self._has_source_file = False
        self._has_input_file = False
        self._source_file = '-'
        self._input_file = '-'

    def print_help(self):
        print("usage: interpret.py [-h] (--source SOURCE | --input INPUT)\n\n"
              "optional arguments:\n"
              "  -h, --help       show this help message and exit\n"
              "  --source SOURCE  Source file with XML of source code\n"
              "  --input INPUT    File with input for interpret")
        exit(0)    

    def process_args(self):
        for arg in sys.argv:            
            if arg == '-h' or arg == '--help':
                self._will_print_help = True

            input = re.search(r"(?<=--input=)\S+", arg)
            if input:
                input = input.group()
                file_validity(input, 'input')                   
                self._has_input_file = True
                self._input_file = input

            source = re.search(r"(?<=--source=)\S+", arg)
            if source:
                source = source.group()
                file_validity(source, 'source') 
                self._has_source_file = True
                self._source_file = source

        if self._will_print_help:
            self.print_help()

        missing_both_files = (not self._has_input_file) and (not self._has_source_file)
        if missing_both_files:
            print("Error: one of the arguments --source --input is required", file=sys.stderr)
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
        
def args_process():
    args = Arguments()
    args.process_args()
    return args


def main():
    args = args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        print(input_file.read())
        print(source_file.read())

if __name__=="__main__":
    main()