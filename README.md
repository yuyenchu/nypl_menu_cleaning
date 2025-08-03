# nypl_menu_cleaning

## Installation
1. Download and install [docker](https://docs.docker.com/engine/install/ubuntu/), preferably on a Linux system
1. Download [NYPL-menu dataset](https://www.nypl.org/research/support/whats-on-the-menu)

## Setup
1. For users who want to host python containers, run
    ```
    docker compose up -d --build
    ```
1. For users who want to connect to running container, run
    ```
    sudo chmod +x connect.sh
    ./connect.sh
    ```
    then copy the public key content displayed, send the key to the host machine under the `keys` folder, after restart containers, run
    ```
    ./connect.sh HOST_NAME HOST_PORT
    ```
    after you're connected, you can access vscode server at `http://localhost:8080`
1.  Within the container, you will find the src folder of this repo under `/home/dev/src`, then upload your unzipped dataset into the container

## Usage
- profile dataset
    ```shell
    python src/profile.py -p PATH_TO_DATASET_FOLDER
    ```
- create and insert all data
    ```shell
    python src/test.py -p PATH_TO_DATASET_FOLDER --reset
    ls *.npy  # row ids of failed insert to table
    cat test.log # the log output of the create and insert
    ```
- run all test
    ```shell
    python src/test.py -p PATH_TO_DATASET_FOLDER --tests all
    ls *.json  # row ids of failed testcases
    cat test.log # the log output of the test
    ```
    or alternatively use `pytest` (less support for file outputs)
    ```shell
    pytest src/tests
    ```
- clean dataset
    ```shell
    python src/clean.py -i PATH_TO_DIRTY_DATASET_FOLDER -o PATH_TO_CLEAN_DATASET_FOLDER -t PATH_TO_DIRTY_TEST_OUTPUT_FOLDER
    ```
- report and view data change
    ```shell
    python src/report_change.py -d PATH_TO_DIRTY_DATASET_FOLDER -c PATH_TO_CLEAN_DATASET_FOLDER 
    ```