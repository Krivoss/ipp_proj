<?php
/**
* @file test.php
* @author Jakub Krivanek (xkriva30), FIT
* @date April 2022 (academic year 2021/2022)
* @brief Testing program for parse.php and interpret.py
*/

$prog_args = arg_check();

// var_dump($prog_args);

$tests = test($prog_args);
$tests->print_results_to_html();

//                        FUNCTIONS

function arg_check() {
    $args = getopt('h', array("help::", "directory::", "recursive::", "parse-script::",
        "int-script::", "parse-only::", "int-only::", "jexampath::", "noclean::"));

    $prog_args = new prog_arguments();
    foreach ($args as $option => $value) {
        switch ($option) {
            case 'h':
            case 'help':
                foreach ($args as $option => $value) {
                    if ($option != 'h' && $option != 'help') {
                        fwrite(STDERR, "Error: cannot combine -h or --help with other arguments\n");
                        exit(10);
                    }
                }
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
            case 'directory':
                $prog_args->set_directory($value);
                break;
            case 'recursive':
                $prog_args->recursive();  
                break;
            case 'parse-script':
                $prog_args->set_parse_script($value);
                break;
            case 'int-script':
                $prog_args->set_int_script($value);
                break;            
            case 'parse-only':
                $prog_args->set_mode('parse-only');  
                break;
            case 'int-only':
                $prog_args->set_mode('int-only');  
                break;
            case 'jexampath':
                $prog_args->set_jexam($value);
                break;
            case 'noclean':
                $prog_args->noclean();
                break;
            default:
                printf("Argument processing fail\n");
                exit(99);
                break;
        }
    }
    return $prog_args;
}

function test($prog_args) {
    $tests = get_tests($prog_args);
    foreach ($tests->get_tests() as $test) {
        if ($prog_args->get_mode() == 'parse-only') {
            $test->parse($prog_args, $tests, false);
        }
        elseif ($prog_args->get_mode() == 'int-only') {
            $test->interpret($prog_args, $tests);
        }
        else {
            $test->parse_and_interpret($prog_args, $tests);
        }
        if($prog_args->get_noclean() == false) {
            $command = "rm -f ".$test->get_name().".tmp ".$test->get_name().".tmp.out";
            exec($command);
        }
    }
    return $tests;
}

function get_tests($prog_args) {
    if ($prog_args->recursive) {
        try {
            $o_dir = new RecursiveDirectoryIterator($prog_args->get_directory());
        }
        catch (Exception) {
            fwrite(STDERR, "Error: Failed to open directory: No such file or directory \n");
            exit(41);
        }            
        $o_iter = new RecursiveIteratorIterator($o_dir);        
    }
    else {
        try {
            $o_dir = new DirectoryIterator($prog_args->get_directory());
        }
        catch (Exception) {
            fwrite(STDERR, "Error: Failed to open directory: No such file or directory \n");
            exit(41);
        }
        $o_iter = new IteratorIterator($o_dir);        
    }
    $tests = new test_set;
    foreach ($o_iter as $o_info) {
        if ($o_info->getExtension() == 'src') {
            $name = substr($o_info->getPathname(), 0, -4);
            $new_test =  new test($name);
            $tests->add_test($new_test);
        }
    }
    return $tests;
}

//                        CLASSES
class prog_arguments {
    public $mode;
    public $directory;
    public $parse_script;
    public $int_script;
    public $recursive;
    public $jexam;
    public $noclean;

    function __construct() {
        $this->mode = 'both';
        $this->directory = "./";
        $this->parse_script = "parse.php";
        $this->int_script = "interpret.py";
        $this->recursive = false;
        $this->jexam = "/pub/courses/ipp/jexamxml/jexamxml.jar";
        $this->noclean = false;
    }

    function set_directory($directory) {
        $this->directory = $directory;
    }

    function set_parse_script($parse_script) {
        $this->parse_script = $parse_script;
    }

    function set_int_script($int_script) {
        $this->int_script = $int_script;
    }

    function set_jexam($jexam_path) {
        $this->jexam = $jexam_path."jexamxml.jar";
    }

    function recursive() {
        $this->recursive = true;
    }

    function noclean() {
        $this->noclean = true;
    }

    function set_mode($mode) {
        $this->mode = $mode;
    }

    function get_mode() {
        return $this->mode;
    }

    function get_directory() {
        return $this->directory;
    }

    function get_parse_script() {
        return $this->parse_script;
    }

    function get_int_script() {
        return $this->int_script;
    }

    function get_jexam() {
        return $this->jexam;
    }

    function get_noclean() {
        return $this->noclean;
    }
}

class test {
    public $name;
    public $src_file;
    public $in_file;
    public $out_file;
    public $rc_file;
    public $tmp_file;

    public $ref_rc;
    public $my_rc;

    public $has_passed;

    function __construct($name) {
        $this->name = $name;
        $this->get_files();
    }

    function set_name($name) {
        $this->name = $name;
    }

    function set_has_passed($has_passed) {
        $this->has_passed = $has_passed;
    }

    function get_has_passed() {
        return $this->has_passed;
    }

    function get_files() {
        $this->src_file = $this->name.".src";
        $this->in_file = $this->name.".in";
        $this->out_file = $this->name.".out";
        $this->rc_file = $this->name.".rc";
        $this->tmp_file = $this->name.".tmp";

        if(!is_file($this->in_file)){
            $contents = '';
            file_put_contents($this->in_file, $contents);
        }
        if(!is_file($this->out_file)){
            $contents = '';
            file_put_contents($this->out_file, $contents);
        }
        if(!is_file($this->rc_file)){
            $contents = "0\n";
            file_put_contents($this->rc_file, $contents);
        }
    }

    function get_src_file() {
        return $this->src_file;
    }

    function get_name() {
        return $this->name;
    }

    function get_ref_rc() {
        return $this->ref_rc;
    }

    function read_ref_rc() {
        $this->ref_rc = trim(file_get_contents($this->rc_file), "\n");
        return $this->ref_rc;
    }

    function set_my_rc($my_rc) {
        $this->my_rc = $my_rc;
    }

    function get_my_rc() {
        return $this->my_rc;
    }

    function parse($prog_args, $tests, $before_interpret) {
        $file = $this->get_name();
        $out;
        $parse_ret;
        $result;
        $command = "php8.1 ".$prog_args->get_parse_script()." <".$this->src_file." >".$this->tmp_file." 2>/dev/null";
        exec($command, $out, $parse_ret);
        $this->set_my_rc($parse_ret);
        $this->read_ref_rc();
        if ($before_interpret && $parse_ret == 0) {
            $this->set_has_passed(true);
            return true;
        }
        if($parse_ret != $this->ref_rc) {
            $this->set_has_passed(false);
            $tests->add_failed_test($this);
            return false;
        }
        elseif ($parse_ret != 0) {
            $this->set_has_passed(true);
            return true;
        }
        else {            
            $diff_command = "java -jar ".$prog_args->get_jexam()." ".$this->tmp_file." ".$this->out_file." /dev/null options";
            exec($diff_command, $out, $compare_ret);
            if($compare_ret != 0) {
                $this->set_has_passed(false);
                $tests->add_failed_test($this);
                return false;
            }
            else {
                $this->set_has_passed(true);
                return true;
            }
        }
    }

    function interpret($prog_args, $tests) {
        $out;
        $int_ret;
        $result;
        $command = "python3.8 ".$prog_args->get_int_script()." --source=".$this->src_file." --input=".$this->in_file.
                    " >".$this->tmp_file.".out 2>/dev/null";
        
        exec($command, $out, $int_ret);
        $this->set_my_rc($int_ret);
        $this->read_ref_rc();
        $ref_out = file_get_contents($this->out_file);        
        if($int_ret != $this->ref_rc) {
            $this->set_has_passed(false);
            $tests->add_failed_test($this);
        }
        elseif ($int_ret != 0) {
            $this->set_has_passed(true);
        }
        else {
            $diff_command = "diff ".$this->tmp_file.".out ".$this->out_file." >/dev/null";
            exec($diff_command, $out, $compare_ret);
            if($compare_ret != 0) {
                $this->set_has_passed(false);
                $tests->add_failed_test($this);
            }
            else {
                $this->set_has_passed(true);
            }
        }
    }

    function parse_and_interpret($prog_args, $tests) {
        if ($this->parse($prog_args, $tests, true) == false) {
            return;
        }
        $this->src_file = $this->tmp_file;
        $this->interpret($prog_args, $tests);
    }
    
}

class test_set {
    public $tests;
    public $passed;
    public $failed;
    public $failed_tests;

    function __construct() {
        $this->tests = [];
        $this->passed = 0;
        $this->failed = 0;
        $this->failed_tests = [];
    }

    function add_test($test) {
        array_push($this->tests, $test);
    }

    function add_failed_test($test) {
        array_push($this->failed_tests, $test);
    }

    function get_results() {
        foreach ($this->tests as $test) {
            if ($test->get_has_passed() == true) {
                $this->passed++;
            }
            else {
                $this->failed++;
            }
        }
    }

    function get_passed() {
        return $this->passed;
    }

    function get_failed() {
        return $this->failed;
    }

    function get_tests() {
        return $this->tests;
    }

    function print_results_to_console() {
        $this->get_results();
        $passed = $this->get_passed();
        $failed = $this->get_failed();
        echo("TEST RESULTS:\n\t\033[01;32mPASSED: ".$passed."\033[0m\n\t\033[01;31mFAILED: ".$failed."\033[0m\n");
        if (count($this->failed_tests)) {
            $test_paths = [];
            $test_result = [];
            echo "\nFAILED TESTS:\n";
            foreach ($this->failed_tests as $test) {
                $path = "\t".$test->get_name();           
                $result = "\tEXPECTED: ".$test->get_ref_rc()."\tGOT: ".$test->get_my_rc()."\n";
                echo $path.$result;
            }
        }
    }

    function print_results_to_html() {
        $this->get_results();
        $passed = $this->get_passed();
        $failed = $this->get_failed();
        echo "<!DOCTYPE html>\n<html>\n<head>";
        echo '<style>
        .column {
        float: left;
        }
        .left {
        width: 40%;
        }    
        .middle {
        width: 30%;
        }        
        .right {
        width: 30%;
        }    
        .row:after {
        content: "";
        display: table;
        clear: both;
        }
        </style>';
        echo "<title>Test results</title>
        </head>
        <body style=\"background-color:#1e1e1e;\">";
        echo "<h1 style=\"color:white;\">Test results:</h1>
        <h3 style=\"color:white;\">PASSED: ".$passed."</h3>
        <h3 style=\"color:white;\">FAILED: ".$failed."</h3>";
        if (count($this->failed_tests)) {
            $test_paths = [];
            $test_ref_rc = [];
            $test_my_rc = [];
            foreach ($this->failed_tests as $test) {
                array_push($test_paths, $test->get_name());
                array_push($test_ref_rc, $test->get_ref_rc());
                array_push($test_my_rc, $test->get_my_rc());
            }    
            $div1 = '<div class="row">
                    <h1 style="color:red;">Failed tests:</h1>
                        <div class="column left">
                            <h2 style="color:white;">Test paths</h2>';
            $div2 = '</div>
                        <div class="column middle">
                            <h2 style="color:white;">Expected rc</h2>';
            $div3 = '</div>
                        <div class="column right">
                            <h2 style="color:white;">Got rc</h2>';                        
            $div4 = '</div>
                    </div>';
            for ($i = 0; $i < count($test_paths); $i++) {
                $div1 = $div1.'<p style="color:white;">'.$test_paths[$i].'</p>';
                $div2 = $div2.'<p style="color:white;">'.$test_ref_rc[$i].'</p>';
                $div3 = $div3.'<p style="color:white;">'.$test_my_rc[$i].'</p>';
            }
            echo $div1.$div2.$div3.$div4;
        }
        else {
            echo "<h1 style=\"color:green;\">ALL PASSED</h1>";
        }
        echo "</body>\n</html>";
    }
}

?>
