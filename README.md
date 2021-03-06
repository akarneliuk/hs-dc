# Hyper Scaler DC
There are plenty of technical challenges associated with the build of the hyper-scalre infrastructure, which exists behind some biggest infrastructures hosting cloud platforms. This repo makes attempt to recreate at high-level the design of such a data centre.

## Used platforms
### Data Centre
- Mellanox P4-switch
- Microsoft Azure SONiC
- Nokia SRLinux

### Development host
- Linux: CentOS 7/8.1
- Containers: Docker 19.03.8
- Automation and orchestartion: Python 3.8
- Graph modelling: NetworkX 2.4
- Visualisation: Graphviz 2.40.1

## Structure
Main components:
- The `topology` directory contains the files with the samle of the of physical and logical topology of the micro pod.
- The `infrastructure` directory contains the directors with the files of the switches running Microsot Azure SONiC

## To-do list
The following ideas are in the pipeline to be implmeneted:
- Automated rollout and provisioning of the network based on graph topology and YAML descriptors
- High-scale fabric with DC aggregarion spine
- Mutiple vendors leafs (Arista EOS, Cumulus Linux, Cisco Nexus) and interop
- Monitoring (tbd)

## Change log
Release `0.5.2`:
- Fixed bug with improper calculation of the fabric IP addresses.

Release `0.5.1`:
- Added the coditionals to the build of the network graph so that it verifies if the devices' types are presented in the `inventory/build.yaml`.
- Added the support for the CentOS 8.
- Fixed bug that the `iface.start` paramter from the inventory wasn't used.

Release `0.5.0`:
- Added the new directory `mix_config`, which contains the configuration files and the sample build of the DC with 2x Nokia SRLinux, 2x Microsoft Azure SONiC, 2x Ubuntu hosts.

Release `0.4.2`:
- Original Bash scripts are moved to `ref_config` folder.
- The debug print statements are removed from the `main.py`.
- Installation of the Docker is added to `prepare.sh`.

Release `0.4.1`:
- Major bug fixing: unique VLANs per SONiC P4 switch are added, now the hosts can communicate to each other without issues

Release `0.4.0`:
- Added the Docker part including creation and management of the Docker containers using Python.
- The `requirements.txt` is modified to add the `docker` library.
- The topology is launched, containers are working fine, likewise the linux bridges. However, the multi-namespace topology inside the P4 switch causes issue (packets are received (host -> bridge -> switch/ns:sw_net -> switch), but not replied)

Release `0.3.2`:
- Added flexible subnet mask for the customer's prefix
- Minor bug fixing

Release `0.3.1`:
- The package `jinja2` is added to allow the templating of the devices configuration.
- The original content of the `infrastructure` directory is moved to `ref_config`, whereas the `infrastructure` is used for dynamically generated config.
- Added logic to build extensive dictionary necessary to provision the network functions.
- The configuration files for the `microsoft-sonic` nodes are generated automatically.

Release `0.3.0`:
- Primitives contain new parameter `templates`, which stores the necessary templates or fixed files for device launch.
- Added functionality to create necessary folders per the template from primitives
- Added templates for `microsoft-sonic` primitive.

Release `0.2.3`:
- The user-defined Python functions are moved to a separate file called `localfunctions.py` in the `bin` directory.

Release `0.2.2`:
- Added the IP addresses attribute to the nodes: `ipv4` for ports and `loopback` for switches.
- Changed the colour for the `node-port` and `port-port` edges.
- Added the rank to level the devices on the drawing, but that doesn't work as expected.
- Added `netaddr` library to `requirements.txt` and to the code.

Release `0.2.1`:
- Added `resource.yaml` file in `inventory` directory. It contains some logical resources (BGP ASN, IP addresses), which are used in the topolgy graph build.
- Added the attribute `bgp_asn` to the node containing the switches. It is automaticaly calculated to be unique per each network device.
- Interfaces are created as nodes. So now the grap view is changed. The full link between devices looks like as `dev_a -- port -- port -- dev_b`.

Release `0.2.0`:
- The generation of a network graph is taken from the Graphviz module to NetworkX as it allows to do math operations on graph.
- The Graphviz is used only for visualisation of the graph, not for its build.
- The content of the `requirements.txt` is changed.
- The original `main.py` is moved to `backup` folder and is named now `main013.py`. Same is done for `requirements.txt`.
- The Bash script `prepare.sh` also installs the `graphviz-devel` package necessary for Python's `pygraphviz` to work.

Release `0.1.3`:
- Modifying the colouring so that each pod and each aggs have their own colours.

Release `0.1.2`:
- Changing the colouring of the nodes.
- Changed the pod structure per the blogpost (HS. Part 2.).

Release `0.1.1`:
- Added the `inventory` folder containing the information for the topology generation.
- The intend topology is stored in `inventory/build.yaml`.
- The Bash script `prepare.sh` installs the Graphviz software from the original repository. The version for CentOS is used, so may requre changes if you use another operation system.
- The visualisation of the topology is done using the `pydot` and `graphviz` modules for Python. The autogenerated topology is stored in `topology` folder in both `dot` and `png` formats.

## Additional resources
- NetworkX: https://networkx.github.io
- Graphviz: http://graphviz.org
- jinja2: https://jinja.palletsprojects.com/
- Docker: https://docker-py.readthedocs.io/

# Do you want to automate network like a profi?
Join the network automation course: http://training.karneliuk.com

(c) 2016-2020 karneliuk.com
