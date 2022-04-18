'''
    File name: interpret_scopes.py
    Author: Jakub Krivanek (xkriva30), FIT
    Date: April 2022 (academic year 2021/2022)
    Python Version: 3.8
    Brief: File with classes for interpret scopes and variables
'''

import sys

import interpret_fuctions as i_func

class variable:
    """
    A class to represent a variable
    """
    def __init__(self, value = None, var_type = ''):
        self.value = value
        self.var_type = var_type
        self.initialized = False
    
    def get_value(self, instr):
        if self.initialized:
            return self.value
        else:
            instr.error_exit(56, f"variable not initialized")

    def get_type(self):
        return self.var_type

    def set_value(self, value, var_type):
        if var_type == 'string':
            value = i_func.str_escape(value)
        self.value = value
        self.var_type = var_type
        self.initialized = True    

class scope:
    """
    A class to represent a scope
    """
    def __init__(self, scope_type):
        self.var_list = {}
        self.scope_type = scope_type

    def define_var(self, instr, name) -> None:
        if name in self.var_list:
            instr.error_exit(52, f"{self.scope_type}@{name} already defined")
        else:
            self.var_list[name] = variable()  
    
    def get_var(self, instr, name) -> variable:
        if name not in self.var_list:
            instr.error_exit(54, f"{self.scope_type}@{name} not defined")
        else:
            return self.var_list[name]
    
    def set_scope(self, scope_type) -> None:
        self.scope_type = scope_type  

    def set_var(self, instr, name, value, var_type) -> None:
        if name not in self.var_list:
            instr.error_exit(54, f"{self.scope_type}@{name} not defined")
        else:
            self.var_list[name].set_value(value, var_type)

class program_scopes:
    """
    A class to represent scopes, stack and return stack
    """
    def __init__(self):
        self.gf_scope = scope('GF')
        self.tf_scope = None
        self.lf_scopes = []
        self.stack = []
        self.intr_num = 0
        self.return_stack = []

    def def_var(self, instr, name) -> None:
        """
        Defines variable, frame decided based on variable prefix 
        """
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.__def_gf_var(instr, var_name)
        elif scope_prefix == 'LF':
            return self.__def_lf_var(instr, var_name)
        elif scope_prefix == 'TF':
            return self.__def_tf_var(instr, var_name)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    def get_var(self, instr, name) -> variable:
        """
        Returns variable with given name
        """
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.__get_gf_var(instr, var_name)
        elif scope_prefix == 'LF':
            return self.__get_lf_var(instr, var_name)
        elif scope_prefix == 'TF':
            return self.__get_tf_var(instr, var_name)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)
        

    def set_var(self, instr, name, value, value_type) -> None:
        """
        Sets value to a variable with given name
        """
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.__set_gf_var(instr, var_name, value, value_type)
        elif scope_prefix == 'LF':
            return self.__set_lf_var(instr, var_name, value, value_type)
        elif scope_prefix == 'TF':
            return self.__set_tf_var(instr, var_name, value, value_type)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    # frame methods
    def createframe(self) -> None:
        self.tf_scope = scope('TF')

    def pushframe(self, instr) -> None:
        if self.tf_scope:
            self.tf_scope.set_scope('LF')
            self.lf_scopes.append(self.tf_scope)
            self.tf_scope = None
        else:
            instr.error_exit(55, f"pushing non existent TF")
    
    def popframe(self, instr) -> None:
        if len(self.lf_scopes) > 0:
            self.lf_scopes[-1].set_scope('LF')
            self.tf_scope = self.lf_scopes[-1]
            self.lf_scopes.pop()
        else:
            instr.error_exit(55, f"popping non existent LF")

    # stack methods
    def push_stack(self, var : variable) -> None:
        self.stack.append(var)

    def pop_stack(self, instr) -> variable:
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            instr.error_exit(56, f"popping empty stack")

    # methods for program flow
    def get_instr_num(self) -> int:
        return self.intr_num

    def inc_instr_num(self) -> None:
        self.intr_num += 1
    
    def set_intr_num(self, num : int) -> None:
        self.intr_num = num

    def get_return_num(self, instr) -> int:
        if len(self.return_stack):
            ret = int(self.return_stack[-1])
            self.return_stack.pop()
            return ret
        else:
            instr.error_exit(56, f"return without call")
    
    def set_return_num(self, num : int) -> None:
        self.return_stack.append(str(num))
        
    # methods working with specific frames
    def __get_lf(self, instr) -> scope:
        if self.lf_scopes:
            return self.lf_scopes[-1]
        else:
            instr.error_exit(55, f"LF does not exist")

    def __get_tf(self, instr) -> scope:
        if self.tf_scope:
            return self.tf_scope
        else:
            instr.error_exit(55, f"TF does not exist")    

    def __get_gf(self) -> scope:
        return self.gf_scope

    # Variables in frames
    # LF VAR    
    def __def_lf_var(self, instr, name) -> None:
        lf = self.__get_lf(instr)
        lf.define_var(instr, name)
    
    def __get_lf_var(self, instr, name) -> variable:
        lf = self.__get_lf(instr)
        return lf.get_var(instr, name)        

    def __set_lf_var(self, instr, name, value, value_type) -> None:
        lf = self.__get_lf(instr)
        lf.set_var(instr, name, value, value_type)

    # TF VAR
    def __def_tf_var(self, instr, name) -> None:
        tf = self.__get_tf(instr)
        tf.define_var(instr, name)
    
    def __get_tf_var(self, instr, name) -> variable:
        tf = self.__get_tf(instr)
        return tf.get_var(instr, name)        

    def __set_tf_var(self, instr, name, value, value_type) -> None:
        tf = self.__get_tf(instr)
        tf.set_var(instr, name, value, value_type)

    # GF VAR
    def __def_gf_var(self, instr, name) -> None:
        self.__get_gf().define_var(instr, name)

    def __get_gf_var(self, instr, name) -> variable:
        gf = self.__get_gf()
        return gf.get_var(instr, name)

    def __set_gf_var(self, instr, name, value, value_type) -> None:
        gf = self.__get_gf()
        gf.set_var(instr, name, value, value_type)
