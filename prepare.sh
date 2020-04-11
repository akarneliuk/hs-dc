#!/usr/bin/env bash

# Download the Graphviz
wget http://rpmfind.net/linux/centos/7.7.1908/os/x86_64/Packages/graphviz-2.30.1-21.el7.x86_64.rpm

# Install the Graphviz
sudo yum localinstall graphviz-2.30.1-21.el7.x86_64.rpm 
