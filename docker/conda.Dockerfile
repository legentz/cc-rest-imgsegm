FROM continuumio/miniconda3
# DEPRECATED
WORKDIR /server

# Create the environment:
COPY server/config ./config
COPY server/model ./model
COPY server/tmp ./tmp
COPY server/server.py .

RUN conda env create -f config/server_conda.yml

# Make RUN commands use the new environment:
RUN echo "conda activate ccserver" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

EXPOSE 5000
# The code to run when container is started:
COPY docker/entrypoint.sh .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

