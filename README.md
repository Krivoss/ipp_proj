# IPP project
---

- author: Jakub Křivánek
- About project
  * Project works is split into three parts. 
  * First part is `parse.php` script which analyzes source code in IPP-code22 (assembly language) and outputs a XML representation of given code.
  * Second part is `interpret.py`. This script takes the XML which parse.php made and interprets it.
  * The last part `test.php` is for testing both previous scripts.

---
## Usage
### parse.php
- The script should be run like this: `php8.1 parse.php [-h] < SOURCE > OUT_XML` 
  * SOURCE 
    - the file with IPP-code22 source code
    - this will be put to the input of the script
  * OUT_XML
    - the file with XML representation of the source code
    - this will be put to the output of the script

### interpret.py
- The script should be run like this: `python3.8 interpret.py [-h] (--source=SOURCE | --input=INPUT)` 

  * --source=SOURCE
    - file with XML of the original source code
  * --input=INPUT
    - input for the runtime of interpretation
  * if either of source or input is not selected the missing data will be read from the standard input
  * result of interpretation is on the standard output

### test.php
- The script should be run like this: `php8.1 test.php [options]`
  * Optional parametrs:
    - --directory=path 
        + Tests will be searched in given directory
    - --recursive 
        + Tests will also be searched recursivly in given directory
    - --parse-script=file 
        + File with script for analysis of source code in IPPcode22
    - --int-script=file 
        + File with XML interpret script
    - --parse-only 
        + Only parser will be tested
    - --int-only 
        + Only interpret will be tested
    - --jexampath=path 
        + Path to jaxamxml.jar file
    - --noclean 
        + Auxilliary files will not be deleted during testing
