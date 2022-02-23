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

function read_input() {
    $header = false;
    $programXML = new SimpleXMLElement("<program></program>");
    $instr_order = 1;
    while($line = fgets(STDIN)) {   
        $line = remove_comments(trim($line, "\n"));
        $line = trim($line, " ");
        $split = explode(' ', $line);

        if(!$header) {
            if($line == ".IPPcode22") {
                $header = true;
                $programXML->addAttribute('language', $line);
            }
        }

        switch(strtoupper($split[0])) {
            case 'DEFVAR':
                $instruction = add_instruction($programXML, $split[0], $instr_order);
                if(is_valid_var($split[1])) {
                    add_arg($instruction, '1', $split[1], 'var');
                }
                else {
                    wrong_operands('DEFVAR');
                }
                break;
            case 'WRITE':
                $instruction = add_instruction($programXML, $split[0], $instr_order);
                if(is_valid_var($split[1])) {
                    add_arg($instruction, '1', $split[1], 'var');
                }
                elseif (is_valid_symb($split[1])) {
                    add_arg($instruction, '1', $split[1], 'symb');
                }
                else {
                    wrong_operands('WRITE');
                }
                break;
        }
        $instr_order++;
    }
    // formating 
    $doc = new DOMDocument();
    $doc->loadXML($programXML->asXML());
    $doc->formatOutput = true;
    echo $doc->saveXML();
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
    return preg_match(("/(LF|GF|TF)@[a-zA-Z#$&*][a-zA-Z#$&*0-9]*/"), $var_n);
}

function is_valid_symb($symb_n) {
    return preg_match(("/(LF|GF|TF|string|bool)@[a-zA-Z#$&*\][a-zA-Z#$&*0-9]*/"), $symb_n);
}


function remove_comments($line) {
    $pos = strpos($line, "#");
    if($pos) {
        $line = substr($line, 0, $pos);
    }
    return $line;
}

?>