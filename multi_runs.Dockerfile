FROM python:3.6.8-slim-stretch AS compile-image

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc apt-utils cmake openssh-client git && \
    apt-get install -y python-dev libhdf5-dev libxml2-dev zlib1g-dev # Needed for igraph && \
    rm -rf /var/cache/apt/* && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN git clone -b aucell_multi_runs_and_fix_empty_motif_data https://github.com/dweemx/pySCENIC.git && \
    cd pySCENIC && \
    pip install .

FROM python:3.6.8-slim-stretch AS build-image
RUN apt-get -y update && \
    # Need to run ps
    apt-get -y install procps && \
    apt-get -y install libxml2 && \
    rm -rf /var/cache/apt/* && \
    rm -rf /var/lib/apt/lists/*

COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"