import sys

import interpret_fuctions as i_func

class variable:
    def __init__(self, value = None, var_type = 'nil'):
        self._value = value
        self._var_type = var_type
        self._initialized = False
    
    def get_value(self, instr):
        if self._initialized:
            return self._value
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"variable not initialezed")

    def set_value(self, value, var_type):
        if var_type == 'string':
            value = i_func.str_escape(value)
        self._value = value
        self._var_type = var_type
        self._initialized = True

    def get_type(self):
        return self._var_type

    def set_type(self, var_type):
        self._var_type = var_type
    
    def value_to_print(self):
        if self._value == True:
            return 'true'
        elif self._value == False:
            return 'false'
        else:
            return self._value

class scope:
    def __init__(self, scope_type):
        self._var_list = {}
        self._scope_type = scope_type
    
    def set_scope(self, scope_type):
        self._scope_type = scope_type

    def define_var(self, instr, name):
        if name in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"{self._scope_type}@{name} already defined")
        else:
            self._var_list[name] = variable()

    def get_scope_var(self, instr, name):
        if name not in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"{self._scope_type}@{name} not defined")
        else:
            return self._var_list[name]

    def set_scope_var(self, instr, name, value, var_type):
        if name not in self._var_list:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"{self._scope_type}@{name} not defined")
        else:
            self._var_list[name].set_value(value, var_type)

class program_scopes:
    def __init__(self):
        self._gf_scope = scope('GF')
        self._tf_scope = None
        self._lf_scopes = []
        self._stack = []
        self._intr_num = 0
        self._return_num = None

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

    def get_var(self, instr, name) -> variable:
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

    def set_var(self, instr, name, value, value_type):
        scope_prefix = name[:2]
        var_name = name[3:]
        if scope_prefix == 'GF':
            return self.set_gf_var(instr, var_name, value, value_type)
        elif scope_prefix == 'LF':
            return self.set_lf_var(instr, var_name, value, value_type)
        elif scope_prefix == 'TF':
            return self.set_tf_var(instr, var_name, value, value_type)
        else:
            print("INTERNAL ERROR: scope detection failed", file=sys.stderr)
            exit(99)

    def createframe(self):
        self._tf_scope = scope('TF')

    def pushframe(self, instr):
        if self._tf_scope:
            self._tf_scope.set_scope('LF')
            self._lf_scopes.append(scope('LF'))
            self._tf_scope = scope('TF')
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 55, f"pushing non existent TF")
    
    def popframe(self, instr):
        if len(self._lf_scopes) > 0:
            self._lf_scopes[-1].set_scope('LF')
            self._tf_scope = self._lf_scopes[-1]
            self._lf_scopes.pop()
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"popping non existent LF")

    def push_stack(self, var : variable):
        self._stack.append(var)

    def pop_stack(self, instr) -> variable:
        if len(self._stack) > 0:
            return self._stack.pop()
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 52, f"popping empty stack")
        
    def get_lf(self, instr):
        if self._lf_scopes:
            return self._lf_scopes[-1]
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 55, f"LF does not exist")

    def get_tf(self, instr):
        if self._tf_scope:
            return self._tf_scope
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 55, f"TF does not exist")    

    def get_gf(self):
        return self._gf_scope

    # LF VAR    
    def def_lf_var(self, instr, name):
        lf = self.get_lf(instr)
        lf.define_var(instr, name)
    
    def get_lf_var(self, instr, name):
        lf = self.get_lf(instr)
        return lf.get_scope_var(instr, name)        

    def set_lf_var(self, instr, name, value, value_type):
        lf = self.get_lf(instr)
        lf.set_scope_var(instr, name, value, value_type)

    # TF VAR
    def def_tf_var(self, instr, name):
        tf = self.get_tf(instr)
        tf.define_var(instr, name)
    
    def get_tf_var(self, instr, name):
        tf = self.get_tf(instr)
        return tf.get_scope_var(instr, name)        

    def set_tf_var(self, instr, name, value, value_type):
        tf = self.get_tf(instr)
        tf.set_scope_var(instr, name, value, value_type)

    # GF VAR
    def def_gf_var(self, instr, name):
        self.get_gf().define_var(instr, name)

    def get_gf_var(self, instr, name):
        gf = self.get_gf()
        return gf.get_scope_var(instr, name)

    def set_gf_var(self, instr, name, value, value_type):
        gf = self.get_gf()
        gf.set_scope_var(instr, name, value, value_type)
        
    def get_instr_num(self):
        return self._intr_num

    def inc_instr_num(self):
        self._intr_num += 1
    
    def set_intr_num(self, num : int):
        self._intr_num = num

    def get_return_num(self, instr):
        if self._return_num:
            return self._return_num
        else:
            i_func.error_exit_on_instruction(instr.get_order(), instr.get_opcode(), 56, f"return without call")
    
    def set_return_num(self, num : int):
        self._return_num = num