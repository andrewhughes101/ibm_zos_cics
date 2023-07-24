#!/bin/bash

set -e

if ! [ -x "$(command -v pip)" ]; then
    echo 'Error: pip is not installed.' >&2
    exit 1
fi

if [ "$VERSION" == "latest" ]; then
    echo "Installing latest Ansible-core..."
    pip install ansible-core
else
    echo "Installing Ansible-core version $VERSION"
    pip install https://github.com/ansible/ansible/archive/$VERSION.tar.gz
fi
