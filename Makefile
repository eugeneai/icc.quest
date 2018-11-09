.PHONY: env dev develop install test edit \
	py pot init-ru update-ru comp-cat \
	upd-cat setup test setup-requs tests \
	run-tests gdb-test clean serve server \
    req req-dev elpy


req: requirements.txt
	pip install -r $<

req-dev: requirements-devel.txt
	pip install -r $<

elpy:
	pip install -r ~/.emacs.d/private/elpy.txt

install: reqs comp-cat
	$(PYTHON) setup.py install

edit:
	cd src && emacs

setup-requs: requirements.txt
	pip install -r requirements.txt

run-tests:
	nosetests -w src/tests

tests:	run-tests

test:	setup run-tests

gdb-test: setup
	gdb --args $(PYTHON) $(VB)/nosetests -w src/tests

py:
	$(PYTHON)
pot:
	mkdir -p $(LCAT)
	$(VB)/pot-create src -o $(LCAT)/messages.pot || echo "Someting unusual with pot."

init-ru:
	$(PYTHON) setup.py init_catalog -l ru -i $(LCAT)/messages.pot \
                         -d $(LCAT)

update-ru:
	$(PYTHON) setup.py update_catalog -l ru -i $(LCAT)/messages.pot \
                            -d $(LCAT)

comp-cat:
	$(PYTHON) setup.py compile_catalog -d $(LCAT)

upd-cat: pot update-ru comp-cat

clean:
	$(PYTHON) setup.py clean

docker: Dockerfile
	docker build -t eugeneai/icc.quest .


server:
	pserve --reload icc.quest.ini

serve: server
