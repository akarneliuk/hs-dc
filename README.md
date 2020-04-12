# Hyper Scaler DC
There are plenty of technical challenges associated with the build of the hyper-scalre infrastructure, which exists behind some biggest infrastructures hosting cloud platforms. This repo makes attempt to recreate at high-level the design of such a data centre.

## Used platforms
### Data Centre
- Mellanox P4-switch
- Microsoft Azure SONiC

### Development host
- Centos 7
- Docker 19.03.8
- Python 3.8
- Graphviz 2.30.1

## Structure
Main components:
- The `topology` directory contains the files with the samle of the of physical and logical topology of the micro pod.
- The `infrastructure` directory contains the directors with the files of the switches running Microsot Azure SONiC

## To-do list
The following ideas are in the pipeline to be implmeneted:
- Automated provisioning of the network based on the dot lines topology and YAML descriptors
- High-scale fabric with DC aggregarion spine
- Mutiple vendors leafs (Arista EOS, Cumulus Linux, Cisco Nexus) and interop
- Monitoring (tbd)

## Change log
Relesase `0.1.1`:
- Added the `inventory` folder containing the information for the topology generation
- The intend topology is stored in `inventory/build.yaml`
- The Bash script `prepare.sh` installs the Graphviz software from the original repository. The version for CentOS is used, so may requre changes if you use another operation system.
- The visualisation of the topology is done using the `pydot` and `graphviz` modules for Python.

# Do you want to automate network like a profi?
Join the network automation course: http://training.karneliuk.com

(c) 2016-2020 karneliuk.com

