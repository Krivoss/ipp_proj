import sys
import re
import operator

import interpret_fuctions as i_func

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
                i_func.file_validity(source, 'source') 
                self._has_source_file = True
                self._source_file = source
            # --input=INPUT
            input = re.search(r"(?<=--input=)\S+", arg)
            if input:
                input = input.group()
                i_func.file_validity(input, 'input')                   
                self._has_input_file = True
                self._input_file = input

        if self._will_print_help:
            i_func.print_help()
            exit(0)

        missing_both_files = (not self._has_input_file) and (not self._has_source_file)
        if missing_both_files:
            i_func.print_help()
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

class program_scopes:
    def __init__(self):
        self._gf_scope = scope('GF')
        self._tf_scope = None
        self._lf_scopes = []

    def def_var(self, instr, name):
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.def_gf_var(instr, var_name)
        elif scope_prefix == 'LF':
            return self.def_lf_var(instr, var_name)
        elif scope_prefix == 'TF':
            return self.def_tf_var(instr, var_name)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    def get_var(self, instr, name):
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.get_gf_var(instr, var_name)
        elif scope_prefix == 'LF':
            return self.get_lf_var(instr, var_name)
        elif scope_prefix == 'TF':
            return self.get_tf_var(instr, var_name)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    def set_var(self, instr, name, value):
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.set_gf_var(instr, var_name, value)
        elif scope_prefix == 'LF':
            return self.set_lf_var(instr, var_name, value)
        elif scope_prefix == 'TF':
            return self.set_tf_var(instr, var_name, value)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    def pop_lf(self, instr):
        if self._lf_scopes:
            self._tf_scope = self._lf_scopes[-1]
            self._lf_scopes.pop()
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"popping empty LF scope", 52)

    def push_lf(self):
        if self._lf_scopes:
            top_lf_scope =  self._lf_scopes[-1]
            top_lf_scope.set_scope('TF')
            self._tf_scope = top_lf_scope
        else:
            self._tf_scope = scope('TF')
        self._lf_scopes.append(scope('LF'))


    def get_lf(self, instr):
        if self._lf_scopes:
            return self._lf_scopes[-1]
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"LF scope does not exist", 55)

    def get_tf(self, instr):
        if self._tf_scope:
            return self._tf_scope
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"TF scope does not exist", 55)    

    def get_gf(self):
        return self._gf_scope

    # LF VAR    
    def def_lf_var(self, instr, name):
        lf = self.get_lf(instr)
        lf.define_var(instr, name)
    
    def get_lf_var(self, instr, name):
        lf = self.get_lf(instr)
        return lf.get_var_value(instr, name)        

    def set_lf_var(self, instr, name, value):
        lf = self.get_lf(instr)
        lf.set_var_value(instr, name, value)

    # TF VAR
    def def_tf_var(self, instr, name):
        tf = self.get_tf(instr)
        tf.define_var(instr, name)
    
    def get_tf_var(self, instr, name):
        tf = self.get_tf(instr)
        return tf.get_var_value(instr, name)        

    def set_tf_var(self, instr, name, value):
        tf = self.get_tf(instr)
        tf.set_var_value(instr, name, value)

    # GF VAR
    def def_gf_var(self, instr, name):
        self.get_gf().define_var(instr, name)

    def get_gf_var(self, instr, name):
        gf = self.get_gf()
        return gf.get_var_value(instr, name)

    def set_gf_var(self, instr, name, value):
        gf = self.get_gf()
        gf.set_var_value(instr, name, value)

class scope:
    def __init__(self, scope_type):
        self._var_list = {}
        self._scope_type = scope_type
    
    def set_scope(self, scope_type):
        self._scope_type = scope_type

    def define_var(self, instr, name):
        if name in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"{self._scope_type}@{name} already defined", 52)
        else:
            self._var_list[name] = variable()

    def get_var_value(self, instr, name):
        if name not in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"{self._scope_type}@{name} not defined", 52)
        else:
            return self._var_list[name].get_var_value()

    def set_var_value(self, instr, name, value):
        if name not in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), f"{self._scope_type}@{name} not defined", 52)
        else:
            self._var_list[name].set_var_value(value)
        
class variable:
    def __init__(self, value = None):
        self._value = value
    
    def get_var_value(self):
        return self._value

    def set_var_value(self, value):
        self._value = value

class argument:
    def __init__(self, type : str, content):
        self._type = type
        self._content = content

    def get_content(self):
        return self._content

    def get_type(self):
        return self._type

class instruction:
    _instr_list = []
    def __init__(self, order : int, opcode : str = None):
        self._order = order
        self._opcode = opcode
        self._instr_list.append(self)

    def get_list(self):
        return self._instr_list
    
    def get_order(self):
        return self._order

    def get_opcode(self):
        return self._opcode

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
    
    def execute(self, scopes):
        scopes.def_var(self, self._arg1.get_content())

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
    
    def execute(self, scopes):
        symb = self._arg1
        symb_type = self._arg1.get_type()
        if symb_type == 'var':
            value = scopes.get_var(self, symb.get_content())
            print(value)
        elif symb_type == 'nil':
            print('', end='')
        else:
            print(symb.get_content(), end='')

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
    
    def execute(self, scopes):
        scopes.set_var(self, self._arg1.get_content(), self._arg2.get_content())

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
            i_func.error_exit_on_instruction(self._order, self._opcode, f"wrong operand types - {op1} {op2}", 53)
        except ZeroDivisionError:
            i_func.error_exit_on_instruction(self._order, self._opcode, "zero devision", 57)
        self._result = res
    
    def execute(self, scopes):
        var = self._arg1
        symb1 = self._arg2
        symb2 = self._arg3
        if symb1.get_type() == 'var':
            symb1_content = scopes.get_var(self, symb1.get_content())
        else:
            symb1_content = symb1.get_content()
        if symb2.get_type() == 'var':
            symb2_content = scopes.get_var(self, symb2.get_content())
        else:
            symb2_content = symb2.get_content()
        self.calc(symb1_content, symb2_content)
        scopes.set_var(self, var.get_content(), self._result)

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
            i_func.error_exit_on_instruction(self._order, self._opcode, f"wrong operand types - {op1} {op2}", 53)
        except IndexError:
            i_func.error_exit_on_instruction(self._order, self._opcode, "index out of range", 58)

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
            i_func.error_exit_on_instruction(order, opcode, f"argument {arg.tag} has no type atribute", 32)
        if arg_type == 'int':
            arg_content = int(arg.text)        
        elif arg_type == 'bool':
            if arg.text == 'true':
                arg_content = True
            else:
                arg_content = False
        elif arg_type == 'var' or arg_type == 'string' or arg_type == 'nil':
            arg_content = arg.text
        return argument(arg.get('type'), arg_content)