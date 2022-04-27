.PHONY: all build clean

DOC=doc
TEST=files_for_testing

all: pack

both_test:
	php8.1 test.php --recursive --directory="tests/both" --jexampath=files_for_testing/ >out.html

pack1: clean
	zip xkriva30.zip -j parse.php test.php interpret*.py $(DOC)/readme1.pdf

pack2: clean
	zip xkriva30.zip -j parse.php test.php interpret*.py $(DOC)/readme1.pdf $(DOC)/readme2.pdf

test_ok1: pack1
	cp xkriva30.zip $(TEST)
	./$(TEST)/is_it_ok.sh xkriva30.zip $(TEST)/test_ok 1

test_ok2: pack2
	cp xkriva30.zip $(TEST)
	./$(TEST)/is_it_ok.sh xkriva30.zip $(TEST)/test_ok 2
	
clean:
	rm -rf xkriva30.zip $(TEST)/xkriva30.zip temp* out.html