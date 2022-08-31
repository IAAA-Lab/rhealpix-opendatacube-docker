# This repository
This repository holds the code that implements the experiments described in ... (give proper citation when available).

## How to use (first time)
I assume that you have docker, docker-compose, 7-zip and make installed and running in your computer. These are the steps you need to follow. They have been tested in Linux (Kubuntu, but they should work in most recent distributions). It should not be difficult to run this in macOS or in a modern Windows with the Windows Subsystem for Linux, and of course you can run it in a Virtual Machine with Linux. If you find any trouble running this, [create an issue](https://github.com/IAAA-Lab/rhealpix-opendatacube-docker/issues) and we will try to help you.

- Clone the repo.
- Run `make setup` (it takes a few minutes). This will:
  - build the jupyter-conda-odc image using the provided `Dockerfile`, just the first time, download other images from docker-hub (just the first time);
  - run the containers from those images (following the `docker-compose.yml`);
- Run `./product-index.sh`. This will:
  - create a directory named data_repo if it does not exist;
  - uncompress the data used in the notebooks (they are compressed and split because some files are too large for GitHub) to that directory;
  - initialize the database for Open Data Cube (this will ask you for your sudo password to delete the previous one); 
  - add the product definitions (they are compressed with the datasets);
  - index the datasets of those products (in the geographic extent defined in the BBOX value defined in the `Makefile`).
- Now you can go to [http://localhost](http://localhost) with the password `secretpassword` and you will see a Jupyter environment with a notebook named `Snow_Cover_Workflow.ipynb`. Open it and run it with the menu `Kernel > Restart & Run All`. You might see some warnings, you can safely ignore them, but every cell in the notebook should run and produce its corresponding output.

## How to use (afterwards)
The next times you want to run the notebook, you may need to run `make up` before you open the Jupyter environment in your web browser.

## History
This repository is partially based on the Cube in a Box by [Open Data Cube](https://www.opendatacube.org).

This started as a fork, but we had to make a number of changes because the original one was not working for us. The main difference is that we are using conda to manage some dependencies, but there are other changes. It is far from ideal to have some dependencies managed with apt-get, others with conda (miniconda actually) and others with pip, but it works.

This repository is also home to the datasets used in the experiments and to the Jupyter notebooks that implement those experiments.

## Credits
This is partially based on <https://github.com/opendatacube/cube-in-a-box> which is:

MIT License

Copyright (c) 2018 Alex Leith

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
