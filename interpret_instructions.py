'''
    File name: interpret_instructions.py
    Author: Jakub Krivanek (xkriva30), FIT
    Date: April 2022 (academic year 2021/2022)
    Python Version: 3.8
    Brief: File with classes for interpret instructions and arguments
'''

import operator
import sys

import interpret_scopes as i_scopes
import interpret_fuctions as i_func

class argument:
    """
    A class to represent instruction arguments
    """
    def __init__(self, type : str, content):
        self.type = type
        self.content = content

    def get_value(self, instr):
        value = self.content
        if self.type == 'string':
            value = i_func.str_escape(self.content)
        return value

    def get_type(self):
        return self.type

class instruction:
    """
    A class to represent instruction instructions
    """
    # shared list of all instructions
    instr_list = []
    def __init__(self, order : int, opcode : str = None):
        self.order = int(order)
        self.opcode = opcode
        self.instr_list.append(self)

    def execute(self, scopes :  i_scopes.program_scopes):
        """
        Executes instruction

        Each instruction should implement its own execute method
        """
        self.error_exit(99, "intruction not implemented")

    def error_exit(self, error_code, error_message, *args):
        """
        Prints error to stderr and exits with given error code
        """
        print(f"Error: instruction n.{self.order} {self.opcode}: {error_message}", end='', file=sys.stderr)
        for a in args:
            a = i_func.value_for_print(a)
            print('', a, end='', file=sys.stderr)
        print(file=sys.stderr)
        exit(error_code)
    
    @classmethod
    def run(cls, scopes :  i_scopes.program_scopes, input_file):
        """
        Executes all instructions one by one
        """
        try:
            i = cls.instr_list[scopes.get_instr_num()]
        except IndexError:
            return
        if i.get_opcode() == 'READ':
            i.execute(scopes, input_file)
        else:
            i.execute(scopes)
        scopes.inc_instr_num()
        cls.run(scopes, input_file)  
    
    def sort_instr_list(self):
        """
        Sorts instructions based on order
        """
        i_list = self.get_list()
        i_list.sort(key=lambda x: x.get_order())
        for index, i in enumerate(i_list):
            if index + 1 != len(i_list):
                if i.get_order() == i_list[index+1].get_order():
                    self.error_exit(32, "order duplicate")

    def find_label(self, label : str):
        """
        Return index of given label
        """
        i_list = self.get_list()
        for index, instr in enumerate(i_list):
            if instr.get_opcode() == 'LABEL':
                if instr.get_label_name() == label:
                    return index - 1
        self.error_exit(52, "label not defined -", label)

    def get_list(self):
        return self.instr_list
    
    def get_order(self):
        return self.order

    def get_opcode(self):
        return self.opcode

# no arguments
class no_operands_instr(instruction):
    def __init__(self, order : int):
        super().__init__(order)

class instr_createframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self.opcode = "CREATEFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.createframe()

class instr_pushframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self.opcode = "PUSHFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.pushframe(self)

class instr_popframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self.opcode = "POPFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.popframe(self)

class instr_return(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self.opcode = "RETURN"

    def execute(self, scopes: i_scopes.program_scopes):
        index = scopes.get_return_num(self) - 1
        scopes.set_intr_num(index)

class instr_break(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self.opcode = "BREAK"

    def execute(self, scopes: i_scopes.program_scopes):
        message = "Break info:\n\ton instruction number " + str(scopes.get_instr_num())
        # TODO more break info
        print(message, file=sys.stderr)

# one argument
class one_arg_instr(instruction):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order)       
        self.arg1 = arg1
        
class instr_defvar(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "DEFVAR"
    
    def execute(self, scopes):
        scopes.def_var(self, self.arg1.get_value(self))

class instr_pops(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "POPS"

    def execute(self, scopes: i_scopes.program_scopes):
        var = scopes.pop_stack(self)
        scopes.set_var(self, self.arg1.get_value(self), var.get_value(self), var.get_type())

class instr_pushs(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "PUSHS"

    def execute(self, scopes: i_scopes.program_scopes):
        symb_val = i_func.get_symb_value(self, scopes, self.arg1)
        var = i_scopes.variable()
        var.set_value(symb_val, self.arg1.get_type())
        scopes.push_stack(var)

class instr_write(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "WRITE"
    
    def execute(self, scopes : i_scopes.program_scopes):
        symb_val = i_func.get_symb_value(self, scopes, self.arg1)
        symb_type = i_func.get_symb_type(self, scopes, self.arg1)
        to_print = i_func.value_for_print(symb_val)
        if symb_type == 'nil':
            print('', end='')
        else:
            print(to_print, end='')

class instr_exit(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "EXIT"

    def execute(self, scopes: i_scopes.program_scopes):
        ret_val = i_func.get_symb_value(self, scopes, self.arg1)
        if type(ret_val) == int and ret_val >= 0 and ret_val <= 49:
            exit(ret_val)
        elif type(ret_val) != int:
            self.error_exit(53,  f"wrong operand type -", ret_val)
        else:
            self.error_exit(57,  f"wrong exit code -", ret_val)

class instr_dprint(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "DPRINT"

    def execute(self, scopes: i_scopes.program_scopes):
        val = i_func.get_symb_type(self, scopes, self.arg1)
        to_print = i_func.value_for_print(val)
        print(to_print, end='', file=sys.stderr)      

class instr_call(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "CALL"

    def execute(self, scopes: i_scopes.program_scopes):
        label = self.arg1.get_value(self)
        index = self.find_label(label)
        scopes.set_return_num(self.order)
        scopes.set_intr_num(index)

class instr_label(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "LABEL"
    
    def get_label_name(self):
        return self.arg1.get_value(self)

    def execute(self, scopes: i_scopes.program_scopes):
        i_list = self.get_list()
        for instr in i_list:
            if instr.get_order() > self.order:
                return
            if instr.get_opcode() == 'LABEL':
                if instr.get_label_name() == self.arg1.get_value(self):
                    if instr.get_order() != self.order:
                        self.error_exit(52, f"label already exists -", self.arg1.get_value(self))


class instr_jump(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self.opcode = "JUMP"

    def execute(self, scopes: i_scopes.program_scopes):
        label = self.arg1.get_value(self)
        index = self.find_label(label)
        scopes.set_intr_num(index)

# two arguments
class two_arg_instr(instruction):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order)       
        self.arg1 = arg1
        self.arg2 = arg2

class instr_move(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "MOVE"
    
    def execute(self, scopes):
        symb = i_func.get_symb_value(self, scopes, self.arg2)
        symb_type = i_func.get_symb_type(self, scopes, self.arg2)
        scopes.set_var(self, self.arg1.get_value(self), symb, symb_type)

class instr_int2char(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "INT2CHAR"
    
    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self.arg2)
        try:
            if i_func.get_symb_type(self, scopes, self.arg2) != 'int':
                raise TypeError
            symb = chr(symb)
            scopes.set_var(self, self.arg1.get_value(self), symb, 'string')       
        except ValueError:
            self.error_exit(58, f"invalid value -", symb)
        except TypeError:
            self.error_exit(53, f"wrong operand types -", symb)

class instr_strlen(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "STRLEN"

    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self.arg2)
        if i_func.get_symb_type(self, scopes, self.arg2) != 'string':
            self.error_exit(53, f"wrong operand types -", symb)
        symb = len(symb)
        scopes.set_var(self, self.arg1.get_value(self), symb, 'int')

class instr_type(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "TYPE"
    
    def execute(self, scopes: i_scopes.program_scopes):
        val_type = i_func.get_symb_type_no_err(self, scopes, self.arg2)
        scopes.set_var(self, self.arg1.get_value(self), val_type, 'string')        

class instr_not(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "NOT"
    
    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self.arg2)
        if i_func.get_symb_type(self, scopes, self.arg2) != 'bool':
            self.error_exit(53, f"wrong operand types -", symb)
        symb = not(symb)
        scopes.set_var(self, self.arg1.get_value(self), symb, 'bool')
            

class instr_read(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self.opcode = "READ"

    def execute(self, scopes: i_scopes.program_scopes, input_file):
        try:
            val = input_file.readline()
            if val:
                if val[-1] == "\n":
                    val = val[:-1]                
        except EOFError:
                scopes.set_var(self, self.arg1.get_value(self), 'nil', 'nil')
                return
        read_type = self.arg2.get_value(self)
        if val:            
            try:
                var = self.arg1.get_value(self)
                if read_type == 'string':
                    scopes.set_var(self, var, val, self.arg2.get_value(self))
                elif read_type == 'int':
                    val = int(val)
                    scopes.set_var(self, var, val, self.arg2.get_value(self))
                elif read_type == 'bool':
                    if val.lower() == 'true':
                        val = True
                    else:
                        val = False
                    scopes.set_var(self, var, val, self.arg2.get_value(self))
                else:
                    raise ValueError
            except ValueError:
                scopes.set_var(self, var, 'nil', 'nil')
        else:
            scopes.set_var(self, self.arg1.get_value(self), 'nil', 'nil')

# three arguments
class three_arg_instr(instruction):    
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order)       
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.result = None
        self.instr_operator = None

    def execute(self, scopes : i_scopes.program_scopes, res_type : str):
        symb1_content = i_func.get_symb_value(self, scopes, self.arg2)
        symb2_content = i_func.get_symb_value(self, scopes, self.arg3)
        if self.instr_operator:
            self.process(symb1_content, symb2_content, self.instr_operator)
        else:
            self.process(symb1_content, symb2_content)
        var = self.arg1
        scopes.set_var(self, var.get_value(self), self.result, res_type)

class arithmetic_instr(three_arg_instr):
    def process(self, op1, op2, myoperator):
        if not (type(op1) == int and type(op2) == int):
            self.error_exit(53, f"wrong operand types -", op1, op2)
        try:
            res = int(myoperator(op1, op2))
        except ZeroDivisionError:
            self.error_exit(57, "zero devision")
        self.result = res
    
    def execute(self, scopes : i_scopes.program_scopes):
        super().execute(scopes, 'int')

class instr_add(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "ADD"
        self.instr_operator = operator.add    

class instr_sub(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "SUB"
        self.instr_operator = operator.sub

class instr_mul(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "MUL"
        self.instr_operator = operator.mul

class instr_idiv(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "IDIV"
        self.instr_operator = operator.floordiv

class relation_instr(three_arg_instr):
    def process(self, op1, op2, myoperator):
        try:
            res = myoperator(op1, op2)
        except TypeError:
            self.error_exit(53, f"wrong operand types -", op1, op2)
        self.result = res

    def execute(self, scopes: i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if self.opcode != "EQ" and (symb1_type == 'nil' or symb2_type == 'nil' or symb1_type != symb2_type):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        if self.opcode == "EQ" and (symb1_type != 'nil' and symb2_type != 'nil' and symb1_type != symb2_type):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        super().execute(scopes, 'bool')

class instr_lt(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "LT"
        self.instr_operator = operator.lt

class instr_gt(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "GT"
        self.instr_operator = operator.gt

class instr_eq(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "EQ"
        self.instr_operator = operator.eq

class logical_instr(three_arg_instr):
    def process(self, op1, op2, myoperator):
        try:
            res = myoperator(op1, op2)
        except TypeError:
            self.error_exit(53, f"wrong operand types -", op1, op2)
        self.result = res

    def execute(self, scopes: i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if not (symb1_type == symb2_type and symb1_type == 'bool'):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        super().execute(scopes, 'bool')

class instr_and(logical_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "AND"
        self.instr_operator = operator.and_

class instr_or(logical_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "OR"
        self.instr_operator = operator.or_


class instr_stri2int(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "STRI2INT"

    def process(self, op1, op2):
        try:
            if op2 < 0:
                raise IndexError
            self.result = ord(op1[op2])
        except TypeError:
            self.error_exit(53, f"wrong operand types -", op1, op2)
        except IndexError:
            self.error_exit(58, "index out of range")
        
    def execute(self, scopes : i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if not (symb1_type == 'string' and symb2_type == 'int'):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        super().execute(scopes, 'int')

class instr_concat(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "CONCAT"

    def process(self, op1, op2):
        self.result = op1 + op2
    
    def execute(self, scopes : i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if symb1_type != 'string' or symb2_type != 'string':
            self.error_exit(53, f"wrong operand types -", self.arg1.get_value(self), self.arg2.get_value(self))
        super().execute(scopes, 'string')

class instr_getchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "GETCHAR"

    def process(self, op1, op2):
        if not (type(op1) == str and type(op2) == int):
            self.error_exit(53, f"wrong operand types -", op1, op2)
        try:
            if op2 < 0:
                raise IndexError
            self.result = ord(op1[op2])
        except IndexError:
            self.error_exit(58, "index out of range")
        self.result = op1[op2]
    
    def execute(self, scopes : i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if symb1_type != 'string' or symb2_type != 'int':
            self.error_exit(53, f"wrong operand types -", self.arg1.get_value(self), self.arg2.get_value(self))
        super().execute(scopes, 'string')

class instr_setchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "SETCHAR"

    def process(self, var, op1, op2):
        if not (type(var) == str and type(op1) == int and type(op2) == str):
            self.error_exit(53, f"wrong operand types -", op1, op2)
        try:
            if op1 < 0 or op1 >= len(var):
                raise IndexError
            if len(op2) <= 0:
                self.error_exit(58, "empty string")
            var = var[:op1] + op2[0] + var[op1+1:]
        except IndexError:
            self.error_exit(58, "index out of range")
        self.result = var
    
    def execute(self, scopes : i_scopes.program_scopes):
        var_val = i_func.get_symb_value(self, scopes, self.arg1)
        symb1_val = i_func.get_symb_value(self, scopes, self.arg2)
        symb2_val = i_func.get_symb_value(self, scopes, self.arg3)
        var_type = i_func.get_symb_type(self, scopes, self.arg1)
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if var_type != 'string' or symb1_type != 'int' or symb2_type != 'string':
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        self.process(var_val, symb1_val, symb2_val)
        scopes.set_var(self, self.arg1.get_value(self), self.result, 'string')

class instr_jumpifeq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "JUMPIFEQ"

    def execute(self, scopes: i_scopes.program_scopes):
        condition = False
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if (symb1_type != 'nil' and symb2_type != 'nil' and symb1_type != symb2_type):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        symb1_val = i_func.get_symb_value(self, scopes, self.arg2)
        symb2_val = i_func.get_symb_value(self, scopes, self.arg3)
        if symb1_val == symb2_val:
            condition = True
        label = self.arg1.get_value(self)
        index = self.find_label(label)
        if condition:
            scopes.set_intr_num(index)

class instr_jumpifneq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self.opcode = "JUMPIFNEQ"

    def execute(self, scopes: i_scopes.program_scopes):
        condition = False
        symb1_type = i_func.get_symb_type(self, scopes, self.arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self.arg3)
        if (symb1_type != 'nil' and symb2_type != 'nil' and symb1_type != symb2_type):
            self.error_exit(53, f"wrong operand types -", self.arg2.get_value(self), self.arg3.get_value(self))
        symb1_val = i_func.get_symb_value(self, scopes, self.arg2)
        symb2_val = i_func.get_symb_value(self, scopes, self.arg3)
        if symb1_val == symb2_val:
            condition = True
        label = self.arg1.get_value(self)
        index = self.find_label(label)
        if not condition:
            scopes.set_intr_num(index)

class factory:
    @classmethod
    def create_instruction(cls, instr):
        """
        Returns created instruction with all arguments
        """
        order = instr.get("order")
        opcode = instr.get("opcode")
        args = {}
        for i in range(1,4):
            arg = instr.findall(f"./arg{i}")
            if len(arg) > 1:
                i_func.error_exit_on_instruction(order, opcode, 32,
                    f"instruction has more arguments with the same number - arg{i}")
            if arg:
                args[f"arg{i}"] = cls.get_argument(arg[0], order, opcode)
        return cls.get_instruction(order, opcode, **args)

    @classmethod
    def get_instruction(cls, order : int, opcode : str,
                arg1 : argument = None, arg2 : argument = None, arg3 : argument = None):
        no_argument = {
            'CREATEFRAME' : instr_createframe,
            'PUSHFRAME' : instr_pushframe,
            'POPFRAME' : instr_popframe,
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
            'JUMP' : instr_jump
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
        opcode = opcode.upper()
        if opcode in no_argument:
            return no_argument[opcode](order)
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
            print(f"Error: instruction n.{order} {opcode}: argument {arg.tag} has no type atribute")
            exit(32)
        if arg_type == 'int':
            arg_content = int(arg.text)        
        elif arg_type == 'bool':
            if arg.text == 'true':
                arg_content = True
            else:
                arg_content = False
        elif arg_type == 'string':
            if arg.text:
                arg_content = arg.text
            else:
                arg_content = ''
        else:
            arg_content = arg.text
        return argument(arg_type, arg_content)
