if [ ! -f "./.vscode-ssh/id_ed25519" ]; then
    mkdir -p ./.vscode-ssh
    ssh-keygen -t ed25519 -f ./.vscode-ssh/id_ed25519 -N ""
    echo "ssh key generated, please copy public key from below to docker host then retry later\n"
    cat ./.vscode-ssh/id_ed25519.pub
else
    ssh -i ./.vscode-ssh/id_ed25519 -L 8080:localhost:8080 dev@$1 -p $2
fi