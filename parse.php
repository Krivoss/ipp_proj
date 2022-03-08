<?php
# init_set('display_errors', 'stderr');

arg_check();

read_input();

//                        FUNCTIONS

function arg_check() {
    $args = getopt('h', ['help']);

    foreach ($args as $option => $value) {
        switch ($option) {
            case 'h':
            case 'help':
                echo("Usage: php8.1 parser.php [options] <inputFile\n");
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

        $instruction;
        if (in_array(strtoupper($split[0]), $instruction_list)) {
            $instruction = add_instruction($programXML, $split[0], $instr_order);
        }
        elseif ($split[0] == '') {
            continue;
        }
        else {
            fwrite(STDERR, "WRONG OR UNKWOWN INSTRUCTION ".$split[0]."\n");
            exit(22);
        }

        switch(strtoupper($split[0])) {
            case 'MOVE':
            case 'INT2CHAR':
            case 'STRLEN':
            case 'TYPE':
                if(count($split) != 3) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1]) && is_valid_symb($split[2])) {
                    add_arg($instruction, '1', $split[1], 'var');
                    add_arg($instruction, '2', $split[2], 'symb');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            case 'CREATEFRAME':
            case 'PUSHFRAME':
            case 'POPFRAME':
            case 'RETURN':
            case 'BREAK':
                if(count($split) != 1) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                break;
            case 'DEFVAR':
            case 'POPS':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1])) {
                    add_arg($instruction, '1', $split[1], 'var');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            case 'CALL':
            case 'LABEL':
            case 'JUMP':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_label($split[1])) {
                    add_arg($instruction, '1', $split[1], 'label');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            case 'PUSHS':
            case 'WRITE':
            case 'EXIT':
            case 'DPRINT':
                if(count($split) != 2) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if (is_valid_symb($split[1])) {
                    add_arg($instruction, '1', $split[1], 'symb');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
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
                    add_arg($instruction, '1', $split[1], 'var');
                    add_arg($instruction, '2', $split[2], 'symb');
                    add_arg($instruction, '3', $split[3], 'symb');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;    
            case 'READ':
                if(count($split) != 3) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if(is_valid_var($split[1]) && is_valid_type($split[2])) {
                    add_arg($instruction, '1', $split[1], 'var');
                    add_arg($instruction, '2', $split[2], 'type');
                }
                else {
                    wrong_operands($split[0]);
                }
                break;
            case 'JUMPIFEQ':
            case 'JUMPIFNEQ':
                if(count($split) != 4) {
                    wrong_num_operands(strtoupper($split[0]));
                }
                if (is_valid_label($split[1]) && is_valid_symb($split[2]) && is_valid_symb($split[3])) {
                    add_arg($instruction, '1', $split[1], 'label');
                    add_arg($instruction, '2', $split[2], 'symb');
                    add_arg($instruction, '3', $split[3], 'symb');
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

function add_arg($instruction, $arg_num, $arg_content, $type) {
    $arg = $instruction->addChild('arg'.$arg_num, $arg_content);
    $arg->addAttribute('type', $type);
    return $arg;
}

function is_valid_var($var_n) {
    return  preg_match(("/(LF|GF|TF)@[a-zA-Z#$&*][a-zA-Z#$&*0-9]*/"), $var_n);
}

function is_valid_symb($symb_n) {
    return preg_match(("/(LF|GF|TF)@[a-zA-Z#$&*\][a-zA-Z#$&*0-9]*/"), $symb_n) |
           preg_match(("/string@*/"), $symb_n) |
           preg_match(("/bool@(true|false)/"), $symb_n) |
           preg_match(("/int@[0-9]+/"), $symb_n);
}

function is_valid_label($label_n) {
    return  preg_match(("/[a-zA-Z#$&*][a-zA-Z#$&*0-9]*/"), $label_n);
}

function is_valid_type($type_n) {
    return  preg_match(("/(int|string|bool)/"), $type_n);
}


?>