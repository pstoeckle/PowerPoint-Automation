#!/bin/bash
# Install bash-completion and add to .bashrc
(   sudo apt-get update -qq \
    && sudo apt-get install -qqy bash-completion \
    && {
    echo 'source /etc/bash_completion' ;
    echo 'source /etc/bash_completion.d/git-prompt' ;
} | tee -a /home/vscode/.bashrc)

# Add code.siemens.com to known hosts
ssh-keyscan github.com | tee -a /home/vscode/.ssh/known_hosts

# Poetry install
poetry install

# Use the Poetry Python in VSCode
jq \
    --arg poetry_stuff "$(poetry run which python)" \
    '.["python.defaultInterpreterPath"] = $poetry_stuff' \
    /home/vscode/.vscode-server/data/Machine/settings.json \
    > /tmp/settings.json \
&& mv /tmp/settings.json /home/vscode/.vscode-server/data/Machine/settings.json
