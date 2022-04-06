import xml.etree.ElementTree as ET

import interpret_classes as i_class
import interpret_fuctions as i_func

def main():
    args = i_func.args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        myroot = ET.parse(source_file).getroot()
        instructions = myroot.findall("./instruction")
        scopes = i_class.program_scopes()
        for instr in instructions:
            order = instr.get("order")
            opcode = instr.get("opcode")
            args = {}
            for i in range(1,4):
                arg = instr.findall(f"./arg{i}")
                if len(arg) > 1:
                    i_func.error_exit_on_instruction(order, opcode, 
                        f"instruction has more arguments with the same number - arg{i}", 32)
                if arg:
                    args[f"arg{i}"] = i_class.factory.get_argument(arg[0], order, opcode)
            instr = i_class.factory.get_instruction(order, opcode, **args)
            instr.execute(scopes)
    

if __name__=="__main__":
    main()