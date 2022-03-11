.PHONY: all build clean

all: pack

pack: clean
	zip -r xkriva30.zip parse.php test.php interpret.py readme1.md

test_ok1: pack
	./is_it_ok.sh xkriva30.zip test_ok 1
	
clean:
	rm -rf xkriva30.zip