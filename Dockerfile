FROM osgeo/gdal:ubuntu-small-3.3.1

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TINI_VERSION=v0.19.0

#ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
#RUN chmod +x /tini

RUN apt-get update && \
    apt-get install -y \
      build-essential \
      git \
      # For Psycopg2
      libpq-dev python3-dev \
      python3-pip \
      wget \
      libgdal-dev \
      libhdf5-serial-dev \
      libnetcdf-dev \
      hdf5-tools \
      netcdf-bin \
      gdal-bin \
      proj-bin \
    && apt-get autoclean \
    && apt-get autoremove \
    && rm -rf /var/lib/{apt,dpkg,cache,log}
    

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && chmod +x Miniconda3-latest-Linux-x86_64.sh \
    && bash ./Miniconda3-latest-Linux-x86_64.sh -b
    
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN conda config --append channels conda-forge \
    && conda create --name odc_env python=3.8 datacube

# conda activate does not work directly as expected. Hence this SHELL command
SHELL ["conda", "run", "-n", "odc_env", "/bin/bash", "-c"]

RUN conda install pyyaml aiohttp requests aiobotocore gdal

# At least some of these are not in conda repos (odc-*) and
# others are there just for the jupyter notebooks
COPY requirements.txt /conf/
RUN pip3 install --no-cache-dir --requirement /conf/requirements.txt

WORKDIR /notebooks

# ENTRYPOINT ["/tini", "--"]

# CMD ["jupyter", "notebook", "--allow-root", "--ip='0.0.0.0'", "--NotebookApp.token='secretpassword'"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "odc_env", "jupyter", "notebook", "--allow-root", "--ip='0.0.0.0'", "--NotebookApp.token='secretpassword'"]
