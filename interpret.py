import xml.etree.ElementTree as ET

import interpret_scopes as i_scopes
import interpret_fuctions as i_func
import interpret_instructions as i_instr


def main():
    args = i_func.args_process()
    with args.get_input_file() as input_file, args.get_source_file() as source_file:
        try:
            myroot = ET.parse(source_file).getroot()
        except ET.ParseError:
            i_func.error_exit_xml_format()
        instructions = myroot.findall("./instruction")
        scopes = i_scopes.program_scopes()
        for instr in instructions:            
            i = i_instr.factory.create_instruction(instr)

        if instructions:
            i.sort_instr_list()
            i.run(scopes, input_file)                    

if __name__=="__main__":
    main()
