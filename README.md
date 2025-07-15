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
    ```
    python src/profile.py -p PATH_TO_DATASET_FOLDER
    ```