FROM eugeneai/python-pyenv

USER python
WORKDIR ${HOME}

# RUN echo $PWD; ls -al /home
ENV PYTHON_CFLAGS "-march=x86-64 -mtune=native -O2 -pipe -fstack-protector-strong -fPIC"

RUN set -e;\
    pyenv install 3.7.1; \
    pyenv rehash

RUN set -e; \
    eval "$(pyenv init -)"; \
    eval "$(pyenv virtualenv-init -)"; \
    pyenv shell 3.7.1; \
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py; \
    python /tmp/get-pip.py; \
    rm -f /tmp/get-pip.py

RUN set -e;\
    eval "$(pyenv init -)"; \
    eval "$(pyenv virtualenv-init -)"; \
    pyenv virtualenv 3.7.1 icc.quest; \
    pyenv rehash; \
    pyenv shell icc.quest; \
    pip install -U pip setuptools

RUN set -e;\
    echo ;\
    git clone --recursive https://github.com/eugeneai/icc.quest;\
    cd ~/icc.quest/; \
    eval "$(pyenv init -)"; \
    eval "$(pyenv virtualenv-init -)"; \
    pyenv rehash; \
    pyenv shell icc.quest; \
    pip install -r requirements-devel.txt; \
    python setup.py develop

# Install AdminLTE interface template
WORKDIR ${HOME}/icc.quest
RUN yay -Sy npm --noconfirm; yes | yay -Scc
RUN set -e;\
    eval "$(pyenv init -)"; \
    eval "$(pyenv virtualenv-init -)"; \
    pyenv rehash;\
    pyenv local icc.quest

RUN cd $(pyenv prefix)/src/isu.webapp/src/isu/webapp; \
    ./install-admin-lte.sh
