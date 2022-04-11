import operator
import sys

import interpret_scopes as i_scopes
import interpret_fuctions as i_func

# TODO get_symb_val/type

class argument:
    def __init__(self, type : str, content):
        self._type = type
        self._content = content

    def get_value(self, instr):
        value = self._content
        if self._type == 'string':
            value = i_func.str_escape(self._content)
        return value

    def get_type(self):
        return self._type

    def value_to_print(self):
        if self._content == True:
            return 'true'
        elif self._content == False:
            return 'false'
        else:
            return self._content

class instruction:
    _instr_list = []
    def __init__(self, order : int, opcode : str = None):
        self._order = int(order)
        self._opcode = opcode
        self._instr_list.append(self)

    def get_list(self):
        return self._instr_list
    
    def get_order(self):
        return self._order

    def get_opcode(self):
        return self._opcode

    def execute(self, scopes :  i_scopes.program_scopes):
        i_func.error_exit_on_instruction(self._order, self._opcode, 99, "intruction not implemented")
    
    def run(self, scopes :  i_scopes.program_scopes, input_file):
        try:
            i = self._instr_list[scopes.get_instr_num()]
        except IndexError:
            return
        if i.get_opcode() == 'READ':
            i.execute(scopes, input_file)
        else:
            i.execute(scopes)
        scopes.inc_instr_num()
        self.run(scopes, input_file)  
    
    def sort_instr_list(self):
        i_list = self.get_list()
        i_list.sort(key=lambda x: x.get_order())
        for index, i in enumerate(i_list):
            if index + 1 != len(i_list):
                if i.get_order() == i_list[index+1].get_order():
                    i_func.error_exit_on_instruction(self._order, self._opcode, 32, "order duplicate")

    def find_label(self, label : str):
        i_list = self.get_list()
        for index, instr in enumerate(i_list):
            if instr.get_opcode() == 'LABEL':
                if instr.get_label_name() == label:
                    return index - 1
        i_func.error_exit_on_instruction(self._order, self._opcode, 52, "label not defined -", label)

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

    def execute(self, scopes: i_scopes.program_scopes):
        index = scopes.get_return_num(self) - 1
        scopes.set_intr_num(index)

class instr_break(no_operands_instr):
    def __init__(self, order : int):
        super().__init__(order)
        self._opcode = "BREAK"

    def execute(self, scopes: i_scopes.program_scopes):
        message = "Break info:\n\ton instruction number " + str(scopes.get_instr_num())
        # TODO more break info
        print(message, file=sys.stderr)

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
        scopes.def_var(self, self._arg1.get_value(self))

class instr_pops(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "POPS"

    def execute(self, scopes: i_scopes.program_scopes):
        var = scopes.pop_stack(self)
        scopes.set_var(self, self._arg1.get_value(self), var.get_value(self), var.get_type())

class instr_pushs(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "PUSHS"

    def execute(self, scopes: i_scopes.program_scopes):
        if self._arg1.get_type() == 'var':
            var = scopes.get_var(self, self._arg1.get_value(self))
            var = i_scopes.variable()
            var.set_value(var.get_value(self), var.get_type())
        else:
            var = i_scopes.variable()
            var.set_value(self._arg1.get_value(self), self._arg1.get_type())
        scopes.push_stack(var)

class instr_write(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "WRITE"
    
    def execute(self, scopes : i_scopes.program_scopes):
        symb = self._arg1
        value_type = self._arg1.get_type()
        if value_type == 'var':
            symb = scopes.get_var(self, symb.get_value(self))
            value_type = symb.get_type()
        to_print = i_func.value_for_print(symb.get_value(self))
        if value_type == 'nil':
            print('', end='')
        else:
            print(to_print, end='')

class instr_exit(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "EXIT"

    def execute(self, scopes: i_scopes.program_scopes):
        ret_val = i_func.get_symb_value(self, scopes, self._arg1)
        if type(ret_val) == int and ret_val >= 0 and ret_val <= 49:
            exit(ret_val)
        elif type(ret_val) != int:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53,  f"wrong operand type -", ret_val)
        else:
            i_func.error_exit_on_instruction(self._order, self._opcode, 57,  f"wrong exit code -", ret_val)

class instr_dprint(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "DPRINT"

    def execute(self, scopes: i_scopes.program_scopes):
        val = i_func.get_symb_type(self, scopes, self._arg1)
        to_print = i_func.value_for_print(val)
        print(to_print, end='', file=sys.stderr)      

class instr_call(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "CALL"

    def execute(self, scopes: i_scopes.program_scopes):
        label = self._arg1.get_value(self)
        index = self.find_label(label)
        scopes.set_return_num(self._order)
        scopes.set_intr_num(index)

class instr_label(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "LABEL"
    
    def get_label_name(self):
        return self._arg1.get_value(self)

    def execute(self, scopes: i_scopes.program_scopes):
        i_list = self.get_list()
        for instr in i_list:
            if instr.get_order() > self._order:
                return
            if instr.get_opcode() == 'LABEL':
                if instr.get_label_name() == self._arg1.get_value(self):
                    if instr.get_order() != self._order:
                        i_func.error_exit_on_instruction(self._order, self._opcode, 52, f"label already exists -", self._arg1.get_value(self))


class instr_jump(one_arg_instr):
    def __init__(self, order : int, arg1 : argument):
        super().__init__(order, arg1)
        self._opcode = "JUMP"

    def execute(self, scopes: i_scopes.program_scopes):
        label = self._arg1.get_value(self)
        index = self.find_label(label)
        scopes.set_intr_num(index)

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
        scopes.set_var(self, self._arg1.get_value(self), self._arg2.get_value(self), self._arg2.get_type())

class instr_int2char(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "INT2CHAR"
    
    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self._arg2)
        try:
            if i_func.get_symb_type(self, scopes, self._arg2) != 'int':
                raise TypeError
            symb = chr(symb)
            scopes.set_var(self, self._arg1.get_value(self), symb, 'string')       
        except ValueError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 58, f"invalid value -", symb)
        except TypeError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", symb)

class instr_strlen(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "STRLEN"

    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self._arg2)
        try:
            if i_func.get_symb_type(self, scopes, self._arg2) != 'string':
                raise TypeError
            symb = len(symb)
            scopes.set_var(self, self._arg1.get_value(self), symb, 'int')
        except TypeError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", symb)

class instr_type(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "TYPE"
    
    def execute(self, scopes: i_scopes.program_scopes):
        val_type = i_func.get_symb_type(self, scopes, self._arg2)
        scopes.set_var(self, self._arg1.get_value(self), val_type, 'string')        

class instr_not(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "NOT"
    
    def execute(self, scopes: i_scopes.program_scopes):
        symb = i_func.get_symb_value(self, scopes, self._arg2)
        try:
            if i_func.get_symb_type(self, scopes, self._arg2) != 'bool':
                raise TypeError
            symb = not(symb)
            scopes.set_var(self, self._arg1.get_value(self), symb, 'bool')
        except TypeError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", symb)

class instr_read(two_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument):
        super().__init__(order, arg1, arg2)
        self._opcode = "READ"

    def execute(self, scopes: i_scopes.program_scopes, input_file):
        try:
            if input_file.name == '<stdin>':
                val = input()
            else:
                val = input_file.readline()
                if val[-1] == "\n":
                    val = val[:-1]
        except EOFError:
                scopes.set_var(self, self._arg1.get_value(self), 'nil', 'nil')
                return
        if val:
            read_type = self._arg2.get_value(self)
            try:
                if read_type == 'string':
                    scopes.set_var(self, self._arg1.get_value(self), val, self._arg2.get_value(self))
                elif read_type == 'int':
                    val = int(val)
                    scopes.set_var(self, self._arg1.get_value(self), val, self._arg2.get_value(self))
                elif read_type == 'bool':
                    if val == 'true':
                        val = True
                    else:
                        val = False
                    scopes.set_var(self, self._arg1.get_value(self), val, self._arg2.get_value(self))
                else:
                    raise ValueError
            except ValueError:
                i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", read_type)
        else:
            scopes.set_var(self, self._arg1.get_value(self), 'nil', 'nil')

# three arguments
class three_arg_instr(instruction):    
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order)       
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3
        self._result = None
        self._instr_operator = None

    def execute(self, scopes : i_scopes.program_scopes, res_type : str):
        symb1_content = i_func.get_symb_value(self, scopes, self._arg2)
        symb2_content = i_func.get_symb_value(self, scopes, self._arg3)
        if self._instr_operator:
            self.process(symb1_content, symb2_content, self._instr_operator)
        else:
            self.process(symb1_content, symb2_content)
        var = self._arg1
        scopes.set_var(self, var.get_value(self), self._result, res_type)

class arithmetic_instr(three_arg_instr):
    def process(self, op1, op2, myoperator):
        if not (type(op1) == int and type(op2) == int):
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", op1, op2)
        try:
            res = int(myoperator(op1, op2))
        except ZeroDivisionError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 57, "zero devision")
        self._result = res
    
    def execute(self, scopes : i_scopes.program_scopes):
        super().execute(scopes, 'int')

class instr_add(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "ADD"
        self._instr_operator = operator.add    

class instr_sub(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "SUB"
        self._instr_operator = operator.sub

class instr_mul(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "MUL"
        self._instr_operator = operator.mul

class instr_idiv(arithmetic_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "IDIV"
        self._instr_operator = operator.floordiv

class relation_instr(three_arg_instr):
    def process(self, op1, op2, myoperator):
        try:
            res = myoperator(op1, op2)
        except TypeError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", op1, op2)
        self._result = res

    def execute(self, scopes: i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self._arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self._arg3)
        i_func.get_symb_value(self, scopes, self._arg2)
        i_func.get_symb_value(self, scopes, self._arg3)
        if symb1_type == 'nil' or symb2_type == 'nil' or symb1_type != symb2_type:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", self._arg1.get_value(self), self._arg2.get_value(self))
        super().execute(scopes, 'bool')

class instr_lt(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "LT"
        self._instr_operator = operator.lt

class instr_gt(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "GT"
        self._instr_operator = operator.gt

class instr_eq(relation_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "EQ"
        self._instr_operator = operator.eq

class instr_and(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "AND"

class instr_or(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "OR"

class instr_stri2int(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "STRI2INT"

    def process(self, op1, op2):
        try:
            if op2 < 0:
                raise IndexError
            self._result = ord(op1[op2])
        except TypeError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", op1, op2)
        except IndexError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 58, "index out of range")
        
    def execute(self, scopes : i_scopes.program_scopes):
        super().execute(scopes, 'int')

class instr_concat(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "CONCAT"

    def process(self, op1, op2):
        self._result = op1 + op2
    
    def execute(self, scopes : i_scopes.program_scopes):
        symb1_type = i_func.get_symb_type(self, scopes, self._arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self._arg3)
        i_func.get_symb_value(self, scopes, self._arg2)
        i_func.get_symb_value(self, scopes, self._arg3)
        if symb1_type != 'string' or symb2_type != 'string':
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", self._arg1.get_value(self), self._arg2.get_value(self))
        super().execute(scopes, 'string')

class instr_getchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "GETCHAR"

    def process(self, op1, op2):
        if not (type(op1) == str and type(op2) == int):
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", op1, op2)
        try:
            if op2 < 0:
                raise IndexError
            self._result = ord(op1[op2])
        except IndexError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 58, "index out of range")
        self._result = op1[op2]
    
    def execute(self, scopes : i_scopes.program_scopes):
        super().execute(scopes, 'string')

class instr_setchar(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "SETCHAR"

    def process(self, var, op1, op2):
        if not (type(var) == str and type(op1) == int and type(op2) == str):
            i_func.error_exit_on_instruction(self._order, self._opcode, 53, f"wrong operand types -", op1, op2)
        try:
            if op1 < 0:
                raise IndexError
            var = var[:op1] + op2 + var[op1+1:]
        except IndexError:
            i_func.error_exit_on_instruction(self._order, self._opcode, 58, "index out of range")
        self._result = var
    
    def execute(self, scopes : i_scopes.program_scopes):
        var = self._arg1
        symb1 = self._arg2
        symb2 = self._arg3
        if symb1.get_type() == 'var':
            symb1_content = scopes.get_var(self, symb1.get_value(self)).get_value(self)
        else:
            symb1_content = symb1.get_value(self)
        if symb2.get_type() == 'var':
            symb2_content = scopes.get_var(self, symb2.get_value(self)).get_value(self)
        else:
            symb2_content = symb2.get_value(self)
        var_content = scopes.get_var(self, var.get_value(self)).get_value(self)
        self.process(var_content, symb1_content, symb2_content)
        scopes.set_var(self, var.get_value(self), self._result, 'string')

class instr_jumpifeq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "JUMPIFEQ"

    def execute(self, scopes: i_scopes.program_scopes):
        condition = False
        symb1_val = i_func.get_symb_value(self, scopes, self._arg2)
        symb2_val = i_func.get_symb_value(self, scopes, self._arg3)
        symb1_type = i_func.get_symb_type(self, scopes, self._arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self._arg3)
        if symb1_type == 'nil' or symb2_type == 'nil':
            condition = True
        elif symb1_type == symb2_type:
            if symb1_val == symb2_val:
                condition = True
        if condition:
            label = self._arg1.get_value(self)
            index = self.find_label(label)
            scopes.set_intr_num(index)

class instr_jumpifneq(three_arg_instr):
    def __init__(self, order : int, arg1 : argument, arg2 : argument, arg3 : argument):
        super().__init__(order, arg1, arg2, arg3)
        self._opcode = "JUMPIFNEQ"

    def execute(self, scopes: i_scopes.program_scopes):
        condition = False
        symb1_val = i_func.get_symb_value(self, scopes, self._arg2)
        symb2_val = i_func.get_symb_value(self, scopes, self._arg3)
        symb1_type = i_func.get_symb_type(self, scopes, self._arg2)
        symb2_type = i_func.get_symb_type(self, scopes, self._arg3)
        if symb1_type == 'nil' or symb2_type == 'nil':
            condition = True
        elif symb1_type == symb2_type:
            if symb1_val == symb2_val:
                condition = True
        if not condition:
            label = self._arg1.get_value(self)
            index = self.find_label(label)
            scopes.set_intr_num(index)

class factory:
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
            i_func.error_exit_on_instruction(order, opcode, 32, f"argument {arg.tag} has no type atribute")
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

    @classmethod
    def create_instruction(cls, instr):
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
