# nypl_menu_cleaning

## Imstallation
- download docker
- download NYPL-menu dataset

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
    python src/profile.py
    ```