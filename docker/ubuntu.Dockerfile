FROM ubuntu:18.04
# DEPRECATED
SHELL [ "/bin/bash", "--login", "-c" ]

# Create a non-root user
ARG username=christian
ARG uid=1000
ARG gid=100

ENV USER $username
ENV UID $uid
ENV GID $gid

ENV HOME /home/$USER
RUN adduser --disabled-password --gecos "Non-root user" --uid $UID --gid $GID --home $HOME $USER

RUN apt update
RUN apt install --assume-yes wget
COPY server/config/server_conda.yml /tmp/
RUN chown $UID:$GID /tmp/server_conda.yml
COPY docker/server_entrypoint.sh /usr/local/bin/
RUN chown $UID:$GID /usr/local/bin/server_entrypoint.sh && chmod u+x /usr/local/bin/server_entrypoint.sh

USER $USER
# install miniconda
ENV CONDA_DIR $HOME/miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && chmod +x ~/miniconda.sh && ~/miniconda.sh -b -p $CONDA_DIR && rm ~/miniconda.sh
# make non-activate conda commands available
ENV PATH=$CONDA_DIR/bin:$PATH
# make conda activate command available from /bin/bash --login shells
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile
# make conda activate command available from /bin/bash --interative shells
RUN conda init bash

# create a project directory inside user home
ENV PROJECT_DIR $HOME/server
RUN mkdir $PROJECT_DIR
WORKDIR $PROJECT_DIR

# build the conda environment
RUN conda update --name base --channel defaults conda && conda env create --file /tmp/server_conda.yml --force && conda clean --all --yes

# copy server folders
COPY server/model ./model
COPY server/tmp ./tmp
COPY server/server.py ./server.py

ENTRYPOINT [ "/usr/local/bin/server_entrypoint.sh" ]

CMD [ "python", "server.py"]

