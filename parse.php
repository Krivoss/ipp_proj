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
                echo("Usage: parser.php [options] <inputFile\n");
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
    while($line = fgets(STDIN)) {
        $line = remove_comments(trim($line, "\n"));    
        $split = explode(' ', trim($line, " "));
        foreach($split as $part) {
            echo($part)."\n";
        }
    }
}

function remove_comments($line) {
    $pos = strpos($line, "#");
    if($pos) {
        $line = substr($line, 0, $pos);
    }
    return $line;
}

?>