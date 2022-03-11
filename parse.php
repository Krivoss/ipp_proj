<?php
/**
* @file parse.php
* @author Jakub Krivanek (xkriva30), FIT
* @date March 2022 (academic year 2021/2022)
* @brief Parses source code IPPcode22 from std input, checks 
*        lexical and syntactic correctness and prints to std output
*        the XML representation of the program
*/

ini_set('display_errors', 'stderr');

arg_check();

read_input();

//                        FUNCTIONS

function arg_check() {
    $args = getopt('h', ['help']);

    foreach ($args as $option => $value) {
        switch ($option) {
            case 'h':
            case 'help':
                echo("Usage: php8.1 parse.php [options] <inputFile >outputFile\n");
                exit(0);
                break;
            default:
                printf("Argument processing fail\n");
                exit(99);
                break;
        }
    }
}

function remove_comments($line) {
    $pos = strpos($line, "#");
    if(!($pos === false)) {
        $line = substr($line, 0, $pos);
    }
    return $line;
}

function xmlEscape($string) {
    return str_replace(array('&', '<', '>', '\'', '"'), array('&amp;', '&lt;', '&gt;', '&apos;', '&quot;'), $string);
}

function read_input() {
    $header = false;
    $programXML = new SimpleXMLElement("<program></program>");
    $instr_order = 1;

    $instruction_list = array('MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL',
                        'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR',
                        'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK', 'WRITE');     

    while($line = fgets(STDIN)) {   
        $line = remove_comments(trim($line, "\n"));
        $line = trim($line, " ");
        $split = explode(' ', $line);

        if(!$header) {
            if($line == ".IPPcode22") {
                $header = true;
                $programXML->addAttribute('language', $line);
                continue;
            }
        }

        $split[0] = strtoupper($split[0]);
        $instruction;
        if (in_array($split[0], $instruction_list)) {
            $instruction = add_instruction($programXML, $split[0], $instr_order);
        }
        elseif ($split[0] == '') {
            continue;
        }
        else {
            fwrite(STDERR, "WRONG OR UNKWOWN INSTRUCTION ".$split[0]."\n");
            exit(22);
        }

        
        switch($split[0]) {
            // <var> <symb>
            case 'MOVE':
            case 'INT2CHAR':
            case 'STRLEN':
            case 'TYPE':
                if(count($split) != 3) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1]) && is_valid_symb($split[2])) {
                    add_arg($instruction, '1', $split[1]);
                    add_arg($instruction, '2', $split[2]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // no operands
            case 'CREATEFRAME':
            case 'PUSHFRAME':
            case 'POPFRAME':
            case 'RETURN':
            case 'BREAK':
                if(count($split) != 1) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                break;
            // <var>
            case 'DEFVAR':
            case 'POPS':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1])) {
                    add_arg($instruction, '1', $split[1]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // <label>
            case 'CALL':
            case 'LABEL':
            case 'JUMP':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_label($split[1])) {
                    add_arg($instruction, '1', $split[1]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // <symb>
            case 'PUSHS':
            case 'WRITE':
            case 'EXIT':
            case 'DPRINT':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if (is_valid_symb($split[1])) {
                    add_arg($instruction, '1', $split[1]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // <var> <symb_1> <symb_2>
            case 'ADD':
            case 'SUB':
            case 'MUL':
            case 'IDIV':
            case 'LG':
            case 'GT':
            case 'EQ':
            case 'AND':
            case 'OR':
            case 'NOT':
            case 'STRI2INT':
            case 'CONCAT':
            case 'GETCHAR':
            case 'SETCHAR':
                if(count($split) != 4) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if (is_valid_var($split[1]) && is_valid_symb($split[2]) && is_valid_symb($split[3])) {
                    add_arg($instruction, '1', $split[1]);
                    add_arg($instruction, '2', $split[2]);
                    add_arg($instruction, '3', $split[3]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // <var> <type>    
            case 'READ':
                if(count($split) != 3) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1]) && is_valid_type($split[2])) {
                    add_arg($instruction, '1', $split[1]);
                    add_arg($instruction, '2', $split[2]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            // <label> <symb_1> <symb_2>
            case 'JUMPIFEQ':
            case 'JUMPIFNEQ':
                if(count($split) != 4) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if (is_valid_label($split[1]) && is_valid_symb($split[2]) && is_valid_symb($split[3])) {
                    add_arg($instruction, '1', $split[1]);
                    add_arg($instruction, '2', $split[2]);
                    add_arg($instruction, '3', $split[3]);
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
        }
        $instr_order++;
    }
    if(!$header) {
        fwrite(STDERR, "WRONG OR MISSING HEADER\n");
        exit(21);
    }
    // formating 
    $doc = new DOMDocument();
    $doc->loadXML($programXML->asXML());
    $doc->encoding='UTF-8';
    $doc->formatOutput = true;
    echo $doc->saveXML();
}

function wrong_num_operands($instr_n) {
    fwrite(STDERR, "WRONG NUMBER OF OPERANDS IN ".$instr_n."\n");
    exit(23);
}

function wrong_operands($instr_n) {
    fwrite(STDERR, "WRONG ".$instr_n." OPERANDS\n");
    exit(23);
}

function add_instruction($programXML, $instr_n, $order) {
    $instruction = $programXML->addChild('instruction');
    $instruction->addAttribute('order', $order);
    $instruction->addAttribute('opcode', $instr_n);
    return $instruction;
}

function add_arg($instruction, $arg_num, $arg_content) {
    $arg = $instruction->addChild('arg'.$arg_num, arg_text_element($arg_content));
    $arg->addAttribute('type', typeofarg($arg_content));
    return $arg;
}

function typeofarg($arg_content) {
    if(preg_match(("/(LF|GF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/"), $arg_content)) {
        return 'var';
    }
    elseif(preg_match(("/string@*/"), $arg_content)) {
        return 'string';
    }
    elseif(preg_match(("/bool@(true|false)$/"), $arg_content)) {
        return 'bool';
    }
    elseif(preg_match(("/int@[-]?[0-9]+$/"), $arg_content)) {
        return 'int';
    }
    elseif(preg_match(("/nil@nil$/"), $arg_content)) {
        return 'nil';
    }
    elseif(preg_match(("/(int|string|bool|nil)$/"), $arg_content)) {
        return 'type';
    }    
    elseif(preg_match(("/[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/"), $arg_content)) {
        return 'label';
    }    
    else {
        exit(99);
    }
}

function arg_text_element($arg_content) {
    $arg_type = typeofarg($arg_content);
    switch($arg_type) {
        case 'var':
        case 'label':
        case 'type':
        case 'nil';
            return xmlEscape($arg_content);
            break;
        default:
            $pos = strpos($arg_content, "@");
            return xmlEscape(substr($arg_content, $pos + 1, strlen($arg_content) - $pos));
            break;            
    }
}

function is_valid_var($var_n) {
    return  preg_match(("/(LF|GF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/"), $var_n);
}

function is_valid_symb($symb_n) {
    return preg_match(("/(LF|GF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/"), $symb_n) |
           preg_match(("/string@*/"), $symb_n) |
           preg_match(("/bool@(true|false)$/"), $symb_n) |
           preg_match(("/int@[-]?[0-9]+$/"), $symb_n) |
           preg_match(("/nil@nil$/"), $symb_n);
}

function is_valid_label($label_n) {
    return  preg_match(("/[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/"), $label_n);
}

function is_valid_type($type_n) {
    return  preg_match(("/(int|string|bool|nil)$/"), $type_n);
}

?>
