# nypl_menu_cleaning

## Installation
- download [docker](https://docs.docker.com/engine/install/ubuntu/)
- download [NYPL-menu dataset](https://www.nypl.org/research/support/whats-on-the-menu)

## Setup
- For users who want to host python containers, run
    ```
    docker compose up -d --build
    ```
- For users who want to connect to running container, run
    ```
    sudo chmod +x connect.sh
    ./connect.sh
    ```
    then copy the public key content displayed, send the key to the host machine under the keys folder, after restart containers, run
    ```
    ./connect.sh HOST_NAME HOST_PORT
    ```

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
    or alternatively use `pytest`
    ```shell
    pytest src/tests
    ```