#!/bin/bash

set -e

version=10.1.0-1.1

wget https://github.com/xpack-dev-tools/riscv-none-embed-gcc-xpack/releases/download/v$version/xpack-riscv-none-embed-gcc-$version-linux-x64.tar.gz

tar -xzvf xpack-riscv-none-embed-gcc-$version-linux-x64.tar.gz
cd xpack-riscv-none-embed-gcc-$version/bin/
./riscv-none-embed-gdb-py3 # check whether it works
# echo "export PATH=\$PATH:`pwd`" >> ~/.bashrc

