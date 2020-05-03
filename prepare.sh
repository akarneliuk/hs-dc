#!/usr/bin/env bash

# Download the Graphviz
wget http://rpmfind.net/linux/centos/7.7.1908/os/x86_64/Packages/graphviz-2.30.1-21.el7.x86_64.rpm

# Install the Graphviz
sudo yum localinstall graphviz-2.30.1-21.el7.x86_64.rpm
sudo yum install -y graphviz-devel

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install docker-ce docker-ce-cli containerd.io

# Lanucn Docker
sudo systemctl start docker.service
