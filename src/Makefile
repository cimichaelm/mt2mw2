# %W% %G%
# File: Makefile
# Last Modification: yy/mm/dd
# Author: Michael Moscovitch
# Description:
# Project:
# History:
#

INSTALL=install
INSTBINFLAGS=-c -m 755
INSTPRVBINFLAGS=-c -m 750
INSTLIBFLAGS=-c -m 644
INSTPRVLIBFLAGS=-c -m 600
INSTDIRFLAGS=-d -m 755
INSTMANFLAGS=-c -m 644
INSTPRVDIRFLAGS=-d -m 750

RM=rm -f
PREFIX=$(HOME)
PHP=php
PHPCHECK=$(PHP) --syntax-check
PYTHON=python
PYTHONCHECK=$(PYTHON) -m py_compile
PYLINT=pylint
YAMLLINT=yamllint
TESTPROG=nose2
PYREVERSE=pyreverse

DESTDIR=$(PREFIX)/bin
BINDIR=$(PREFIX)/bin

APPNAME=mt2mw
MODULE=mt2mw

SCRIPTS=

REQUIREMENTSFILE=requirements.txt

SUBDIRS=

all: build

build: build-setuptools dist-setuptools

build-setuptools:
	python setup.py build

install-setuptools:
	python setup.py install

dist-setuptools:
	python setup.py sdist

test-setuptools:
	python setup.py test


install: install-setuptools install-dirs install-scripts install-config

install-scripts:
	cd scripts; $(MAKE) $@

install-requirements:
	pip install -r $(REQUIREMENTSFILE)

clean:
	$(RM) ./*~ *.pyc *.o
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r $(APPNAME).egg-info

test: test-setuptools

depend:
