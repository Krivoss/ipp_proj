<?php
/**
* @file test.php
* @author Jakub Krivanek (xkriva30), FIT
* @date March 2022 (academic year 2021/2022)
* @brief Testing program for parse.php and interpret.py
*/

arg_check();

parser_test();

//                        FUNCTIONS

function arg_check() {
    $args = getopt('h', ['help']);

    foreach ($args as $option => $value) {
        switch ($option) {
            case 'h':
            case 'help':
                echo("Usage: php8.1 test.php [options]\n\n");
                echo("Options parametrs\n");
                echo("\t--help\t\t\tLists avaible arguments\n");
                echo("\t--directory=path\tTests will be searched in given directory\n");
                echo("\t--recursive\t\tTests will also be searched recursivly in given directory\n");
                echo("\t--parse-script=file\tFile with script for analysis of source code in IPPcode22\n");
                echo("\t--int-script=file\tFile with XML interpret script\n");
                echo("\t--parse-only\t\tOnly parser will be tested\n");
                echo("\t--int-only\t\tOnly interpret will be tested\n");
                echo("\t--jexampath=path\tPath to jaxamxml.jar file\n");
                echo("\t--noclean\t\tAuxilliary files will not be deleted during testing\n");

                exit(0);
                break;
            default:
                printf("Argument processing fail\n");
                exit(99);
                break;
        }
    }
}

function parser_test() {
    $src_files = get_src_files();
    $passed = 0;
    $failed = 0;
    $failed_tests = [];
    foreach ($src_files as $file) {
        $file = str_replace(".src", "", $file);
        $parse_ret = 1;
        $compare_ret = 1;
        $out = array();

        $command = "php8.1 parse.php <".$file.".src >temp.out 2>/dev/null";        
        exec($command, $out, $parse_ret);

        $expected_rc = file_get_contents($file.".rc");
        
        if($parse_ret != $expected_rc) {
            $failed++;
            array_push($failed_tests, $file);
        }
        elseif ($parse_ret != 0) {
            $passed++;
        }
        else {            
            $diff_command = "java -jar jexamxml.jar temp.out ".$file.".out /dev/null options";
            exec($diff_command, $out, $compare_ret);
            if($compare_ret != 0) {
                $failed++;
                array_push($failed_tests, $file);
            }
            else {
                $passed++;
            }
        }
    }
    echo("TEST RESULTS:\n\t\033[01;32mPASSED: ".$passed."\033[0m\n\t\033[01;31mFAILED: ".$failed."\033[0m\n");
    if($failed) {
        echo "\nFAILED TESTS:\n";
        foreach ($failed_tests as $test) {
            echo("\t".$test."\n");
        }
    }    
}

function get_src_files() {
    $o_dir = new RecursiveDirectoryIterator('./GHtests/parse-only');
    $o_iter = new RecursiveIteratorIterator($o_dir);
    $result = [];
    foreach ($o_iter as $o_info) {
        if ($o_info->getExtension() == 'src') {
            array_push($result , $o_info->getPathname());
        }
    }    
    return $result;
}
?>
