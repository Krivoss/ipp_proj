.PHONY: all build clean

all: pack

pack: clean
	zip -r xkriva30.zip parse.php test.php interpret.py readme1.md

clean:
	rm -rf xkriva30.zip