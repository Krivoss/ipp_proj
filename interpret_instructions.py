import operator
import sys

import interpret_scopes as i_scopes
import interpret_fuctions as i_func

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

    def execute(self, scopes :  i_scopes.program_scopes):
        i_func.error_exit_on_instruction(self._order, self._opcode, "intruction not implemented", 99)

# no arguments
class no_operands_instr(instruction):
    def __init__(self, order : int):
        super().__init__(order)

class instr_createframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "CREATEFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.createframe()

class instr_pushframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "PUSHFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.pushframe(self)

class instr_popframe(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "POPFRAME"

    def execute(self, scopes : i_scopes.program_scopes):
        scopes.popframe(self)

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
    
    # TODO writing from var
    def execute(self, scopes : i_scopes.program_scopes):
        symb = self._arg1
        symb_type = self._arg1.get_type()
        if symb_type == 'var':
            value = scopes.get_var(self, symb.get_content())
            print(value, end='')
        elif symb_type == 'nil':
            print('', end='')
        elif symb_type == 'bool':
            if symb.get_content() == True:
                print('true', end='')
            else:
                print('false', end='')
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
    
    def execute(self, scopes : i_scopes.program_scopes):
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
        no_argument = {
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

    @classmethod
    def create_instruction(cls, instr):
        order = instr.get("order")
        opcode = instr.get("opcode")
        args = {}
        for i in range(1,4):
            arg = instr.findall(f"./arg{i}")
            if len(arg) > 1:
                i_func.error_exit_on_instruction(order, opcode, 
                    f"instruction has more arguments with the same number - arg{i}", 32)
            if arg:
                args[f"arg{i}"] = cls.get_argument(arg[0], order, opcode)
        return cls.get_instruction(order, opcode, **args)