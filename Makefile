.PHONY: all build clean

all: pack

both_test:
	php8.1 test.php --recursive --directory="GHtests/both" --jexampath=./ >out.html

pack1: clean
	zip -r xkriva30.zip parse.php test.php interpret*.py readme1.pdf

pack2: clean
	zip -r xkriva30.zip parse.php test.php interpret*.py readme1.pdf readme2.pdf

test_ok1: pack1
	./is_it_ok.sh xkriva30.zip test_ok 1

test_ok2: pack2
	./is_it_ok.sh xkriva30.zip test_ok 2
	
clean:
	rm -rf xkriva30.zip temp* out.html