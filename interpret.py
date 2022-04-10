import xml.etree.ElementTree as ET

import interpret_scopes as i_scopes
import interpret_fuctions as i_func
import interpret_instructions as i_instr


def main():
    args = i_func.args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        myroot = ET.parse(source_file).getroot()
        instructions = myroot.findall("./instruction")
        scopes = i_scopes.program_scopes()
        for instr in instructions:            
            i = i_instr.factory.create_instruction(instr)

        if instructions:
            # sort instruction list by order
            i.get_list().sort(key=lambda x: x.get_order())
            for instr in i.get_list():
                if instr.get_opcode() == 'READ':
                    instr.execute(scopes, input_file)
                else:
                    instr.execute(scopes)

if __name__=="__main__":
    main()