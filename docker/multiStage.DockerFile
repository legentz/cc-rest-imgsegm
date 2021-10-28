# The build-stage image:
FROM continuumio/miniconda3 AS build

# Imposto la cartella che sarà la nuova 'root' del server
WORKDIR /server

# Copio tutti file necessari per runnare il server
COPY server/config ./config

# Creo l'environment utilizzando lo yaml
RUN conda env create -f config/server_conda.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Eseguite solo per scopo di debug conflitti dipendenze
RUN conda list
RUN pip list

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n ccserver -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM debian:buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv
COPY server/model ./model
COPY server/tmp ./tmp
COPY server/server.py .
RUN echo "${PWD}"
# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
           python -c "import flask; print('success!')" && python server.py