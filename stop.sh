#!/bin/bash

sudo docker container kill $(sudo docker container ls --all --quiet)
sudo docker container rm $(sudo docker container ls --all --quiet)

