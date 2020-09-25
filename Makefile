################################################################################
#
#   Makefile for T3
#
################################################################################

install:
	bash devtools/install_t3.sh
	bash devtools/install_pyrms.sh

install-t3:
	bash devtools/install_t3.sh

install-julia:
	bash devtools/install_julia.sh

install-pyrms:
	bash devtools/install_pyrms.sh

test:
	pytest -ra -vv

test-main:
	pytest tests/test_main.py -ra -vv

test-functional:
	pytest tests/test_functional.py -ra -vv
