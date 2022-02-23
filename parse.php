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
                $instruction = $programXML->addChild('instruction');
                $instruction->addAttribute('opcode', $split[0]);
                if(preg_match(("/(LF|GF|TF)@[a-zA-Z#$&*][a-zA-Z#$&*0-9]*/"), $split[1])) {
                    $instructionArg1 = $instruction->addChild('arg1', $split[1]);
                    $instructionArg1->addAttribute('type', 'var');
                }
                else {
                    fwrite(STDERR, "WRONG DEFVAR OPERANDS\n");
                }
        }
    }
    // formating 
    $doc = new DOMDocument();
    $doc->loadXML($programXML->asXML());
    $doc->formatOutput = true;
    echo $doc->saveXML();
}

function remove_comments($line) {
    $pos = strpos($line, "#");
    if($pos) {
        $line = substr($line, 0, $pos);
    }
    return $line;
}

?>