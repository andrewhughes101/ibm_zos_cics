#!/bin/bash

PY_VER=$(python -c 'import platform; print(platform.python_version())')

PY_VER=`echo $PY_VER | sed 's/.[^.]*$//'`

export DEBIAN_FRONTEND=noninteractive

if [[ -L "/usr/bin/python3" ]] && [[ -e "/usr/bin/python3" ]]; then
    rm -f /usr/bin/python3
fi

if (( $(awk 'BEGIN {print ("'$PY_VER'" >= "'3'")}') )); then
    echo "Pythons greater than 3!"
    apt-get update -y && \
    apt-get install -y python${PY_VER}-distutils python${PY_VER}-venv && \
    apt-get update -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/* ;
    ln -f -s /usr/bin/python${PY_VER} /usr/local/bin/python3
    ln -f -s /usr/bin/python${PY_VER} /usr/bin/python3
else
    rm /usr/bin/lsb_release
fi

if [ "$PY_VER" = "3.6" ]; then
    curl -sSo "/tmp/get-pip.py" https://bootstrap.pypa.io/pip/3.6/get-pip.py
elif [ "$PY_VER" = "2.7" ]; then
    curl -sSo "/tmp/get-pip.py" https://bootstrap.pypa.io/pip/2.7/get-pip.py
else
    curl -sSo "/tmp/get-pip.py" https://bootstrap.pypa.io/get-pip.py
fi

python /tmp/get-pip.py
