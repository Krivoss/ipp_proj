import sys
import re
import os.path
import xml.etree.ElementTree as ET
import operator

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

class variable:
    def __init__(self):
        self._value = None
    
    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

class argument:
    def __init__(self, type : str, content):
        self._type = type
        self._content = content

    def get_content(self):
        return self._content

class instruction:
    def __init__(self, order : int, opcode : str = None):
        self._order = order
        self._opcode = opcode
    

# no arguments
class no_operands_instr(instruction):
    def __init__(self, order : int):
        super().__init__(order)

class instr_createframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "CREATEFRAME"

class instr_pushframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "PUSHFRAME"

class instr_popframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "POPFRAME"

class instr_return(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "RETURN"

class instr_break(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "BREAK"

# one argument
class one_arg_instr(instruction):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order)       
        self._arg1 = arg1
        
class instr_defvar(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "DEFVAR"

class instr_pops(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "POPS"

class instr_pushs(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "PUSHS"

class instr_write(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "WRITE"

class instr_exit(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "EXIT"

class instr_dprint(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "DPRINT"       

class instr_call(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "CALL"

class instr_label(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "LABEL"

class instr_jump(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "JUMP"

# two arguments
class two_arg_instr(instruction):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order)       
        self._arg1 = arg1
        self._arg2 = arg2

class instr_move(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "MOVE"

class instr_int2char(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "INT2CHAR"

class instr_strlen(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "STRLEN"

class instr_type(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "TYPE"

class instr_not(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "NOT"

class instr_read(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "READ"

# three arguments
class three_arg_instr(instruction):    
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order)       
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3
        self._result = None
        self._instr_operator = None

    def calc(self, op1, op2, myoperator):
        # op1, op2 = int(op1), int(op2)
        try:
            res = myoperator(op1, op2)
        except TypeError:
            error_exit_on_instruction(self._order, self._opcode, f"wrong operand types - {op1} {op2}", 53)
        except ZeroDivisionError:
            error_exit_on_instruction(self._order, self._opcode, "zero devision", 57)
        print(res)
        self._result = res
    
    def execute(self):
        self.calc(self._arg2.get_content(), self._arg3.get_content())

class instr_add(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "ADD"
        self._instr_operator = operator.add

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)
    

class instr_sub(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "SUB"
        self._instr_operator = operator.sub

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_mul(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "MUL"
        self._instr_operator = operator.mul

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_idiv(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "IDIV"
        self._instr_operator = operator.truediv

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_lt(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "LT"
        self._instr_operator = operator.lt

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_gt(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "GT"
        self._instr_operator = operator.gt

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_eq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "EQ"
        self._instr_operator = operator.eq

    def calc(self, op1, op2):
        super().calc(op1, op2, self._instr_operator)

class instr_and(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "AND"

class instr_or(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "OR"

# OVERIDE
class instr_stri2int(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "STRI2INT"

    def calc(self, op1, op2):
        try:
            res = ord(op1[op2])
            self._result = res
        except TypeError:
            error_exit_on_instruction(self._order, self._opcode, f"wrong operand types - {op1} {op2}", 53)
        except IndexError:
            error_exit_on_instruction(self._order, self._opcode, "index out of range", 58)

class instr_concat(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "CONCAT"

class instr_getchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "GETCHAR"

class instr_setchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "SETCHAR"

class instr_jumpifeq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "JUMPIFEQ"

class instr_jumpifneq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "JUMPIFNEQ"

class factory:
    @classmethod
    def get_instruction(cls, order : int, opcode : str,
                arg1 : argument = None, arg2 : argument = None, arg3 : argument = None):
        no_arguments = {
            'CREATEFRAME' : instr_createframe,
            'PUSHFRAME' : instr_pushframe,
            'RETURN' : instr_return,
            'BREAK' : instr_break
        }
        one_argument = {
            'DEFVAR' : instr_defvar,
            'POPS' : instr_pops,
            'PUSHS' : instr_pushs,
            'WRITE' : instr_write,
            'EXIT' : instr_exit,
            'DPRINT' : instr_dprint,
            'CALL' : instr_call,
            'LABEL' : instr_label,
            'JUMP' : instr_label
        }
        two_arguments = {
            'MOVE':instr_move,
            'INT2CHAR' : instr_int2char,
            'STRLEN' : instr_strlen,
            'TYPE' : instr_type,
            'NOT' : instr_not,
            'READ' : instr_read
        }
        three_arguments = {
            'ADD' : instr_add,
            'SUB' : instr_sub,
            'MUL' : instr_mul,
            'IDIV' : instr_idiv,
            'LT' : instr_lt,
            'GT' : instr_gt,
            'EQ' : instr_eq,
            'AND' : instr_and,
            'OR' : instr_or,
            'STRI2INT' : instr_stri2int,
            'CONCAT' : instr_concat,
            'GETCHAR' : instr_getchar,
            'SETCHAR' : instr_setchar,
            'JUMPIFEQ' : instr_jumpifeq,
            'JUMPIFNEQ' : instr_jumpifneq
        }
        if opcode in no_arguments:
            return one_argument[opcode](order)
        elif opcode in one_argument:
            return one_argument[opcode](order, arg1)
        elif opcode in two_arguments:
            return two_arguments[opcode](order, arg1, arg2)
        elif opcode in three_arguments:
            return three_arguments[opcode](order, arg1, arg2, arg3)
        else:
            print(f"INTERNAL ERROR: factory received invalid opcode {opcode}", file=sys.stderr)
            exit(99)

    @classmethod
    def get_argument(cls, arg, order, opcode):
        arg_type = arg.get('type')
        if not arg_type:
            error_exit_on_instruction(order, opcode, f"argument {arg.tag} has no type atribute", 32)
        return argument(arg.get('type'), arg.text)   

def args_process():
    args = prog_arguments()
    args.process_args()
    return args

def main():
    args = args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        myroot = ET.parse(source_file).getroot()
        instructions = myroot.findall("./instruction")
        for instr in instructions:
            order = instr.get("order")
            opcode = instr.get("opcode")
            args = {}
            for i in range(1,4):
                arg = instr.findall(f"./arg{i}")
                if len(arg) > 1:
                    error_exit_on_instruction(order, opcode, 
                        f"instruction has more arguments with the same number - arg{i}", 32)
                if arg:
                    args[f"arg{i}"] = factory.get_argument(arg[0], order, opcode)
            made_i = factory.get_instruction(order, opcode, **args)
            if(len(args) > 2):
                made_i.execute()
if __name__=="__main__":
    main()