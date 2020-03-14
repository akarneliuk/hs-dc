#!/bin/bash

echo "Launching Docker: starting"
sudo systemctl start docker.service
echo "Launching Docker: done"

echo "Creating the containers: starting"
sudo docker run --net=none --privileged --entrypoint /bin/bash --name leaf11 -it -d -v $PWD/infrastructure/leaf11:/sonic docker-sonic-p4:latest
sudo docker run --net=none --privileged --entrypoint /bin/bash --name leaf12 -it -d -v $PWD/infrastructure/leaf12:/sonic docker-sonic-p4:latest
sudo docker run --net=none --privileged --entrypoint /bin/bash --name spine11 -it -d -v $PWD/infrastructure/spine11:/sonic docker-sonic-p4:latest
sudo docker run --net=none --privileged --entrypoint /bin/bash --name spine12 -it -d -v $PWD/infrastructure/spine12:/sonic docker-sonic-p4:latest
sudo docker run --net=none --privileged --entrypoint /bin/bash --name host11 -it -d ubuntu:14.04 
sudo docker run --net=none --privileged --entrypoint /bin/bash --name host12 -it -d ubuntu:14.04

LEAF11=$(sudo docker inspect --format '{{ .State.Pid }}' leaf11)
LEAF12=$(sudo docker inspect --format '{{ .State.Pid }}' leaf12)
SPINE11=$(sudo docker inspect --format '{{ .State.Pid }}' spine11)
SPINE12=$(sudo docker inspect --format '{{ .State.Pid }}' spine12)
HOST11=$(sudo docker inspect --format '{{ .State.Pid }}' host11)
HOST12=$(sudo docker inspect --format '{{ .State.Pid }}' host12)
echo "Creating the containers: done"

echo "Creating the network connectivity: starting"
sudo brctl addbr s11_l11
sudo ip link set s11_l11 up
sudo ip link add sw_port0 type veth
sudo ip link set veth0 up
sudo brctl addif s11_l11 veth0
sudo ip link set netns ${SPINE11} dev sw_port0
sudo ip link add sw_port5 type veth
sudo ip link set veth1 up
sudo brctl addif s11_l11 veth1
sudo ip link set netns ${LEAF11} dev sw_port5

sudo brctl addbr s12_l11
sudo ip link set s12_l11 up
sudo ip link add sw_port0 type veth
sudo ip link set veth2 up
sudo brctl addif s12_l11 veth2
sudo ip link set netns ${SPINE12} dev sw_port0
sudo ip link add sw_port6 type veth
sudo ip link set veth3 up
sudo brctl addif s12_l11 veth3
sudo ip link set netns ${LEAF11} dev sw_port6

sudo brctl addbr s11_l12
sudo ip link set s11_l12 up
sudo ip link add sw_port1 type veth
sudo ip link set veth4 up
sudo brctl addif s11_l12 veth4
sudo ip link set netns ${SPINE11} dev sw_port1
sudo ip link add sw_port5 type veth
sudo ip link set veth5 up
sudo brctl addif s11_l12 veth5
sudo ip link set netns ${LEAF12} dev sw_port5

sudo brctl addbr s12_l12
sudo ip link set s12_l12 up
sudo ip link add sw_port1 type veth
sudo ip link set veth6 up
sudo brctl addif s12_l12 veth6
sudo ip link set netns ${SPINE12} dev sw_port1
sudo ip link add sw_port6 type veth
sudo ip link set veth7 up
sudo brctl addif s12_l12 veth7
sudo ip link set netns ${LEAF12} dev sw_port6

sudo brctl addbr host11_leaf11
sudo ip link set host11_leaf11 up
sudo ip link add sw_port0 type veth
sudo ip link set veth8 up
sudo brctl addif host11_leaf11 veth8
sudo ip link set netns ${LEAF11} dev sw_port0
sudo ip link add eth1 type veth
sudo ip link set veth9 up
sudo brctl addif host11_leaf11 veth9
sudo ip link set netns ${HOST11} dev eth1

sudo brctl addbr host12_leaf12
sudo ip link set host12_leaf12 up
sudo ip link add sw_port0 type veth
sudo ip link set veth10 up
sudo brctl addif host12_leaf12 veth10
sudo ip link set netns ${LEAF12} dev sw_port0
sudo ip link add eth1 type veth
sudo ip link set veth11 up
sudo brctl addif host12_leaf12 veth11
sudo ip link set netns ${HOST12} eth1
echo "Creating the network connectivity: done"

echo "Configuring hosts: starting"
sudo docker exec -d host11 sysctl net.ipv6.conf.eth0.disable_ipv6=1
sudo docker exec -d host11 sysctl net.ipv6.conf.eth1.disable_ipv6=1
sudo docker exec -d host12 sysctl net.ipv6.conf.eth0.disable_ipv6=1
sudo docker exec -d host12 sysctl net.ipv6.conf.eth1.disable_ipv6=1

sudo docker exec -d host11 ifconfig eth1 192.168.1.2/24 mtu 1400
sudo docker exec -d host11 ip route replace default via 192.168.1.1
sudo docker exec -d host12 ifconfig eth1 192.168.2.2/24 mtu 1400
sudo docker exec -d host12 ip route replace default via 192.168.2.1
echo "Configuring hosts: done"

echo "Configuring switches: starting"
sudo docker exec -d leaf11 ip netns add sw_net
sudo docker exec -d leaf11 ip link set dev sw_port0 netns sw_net
sudo docker exec -d leaf11 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d leaf11 ip netns exec sw_net ip link set sw_port0 up
sudo docker exec -d leaf11 ip link set dev sw_port5 netns sw_net
sudo docker exec -d leaf11 ip netns exec sw_net sysctl net.ipv6.conf.sw_port5.disable_ipv6=1
sudo docker exec -d leaf11 ip netns exec sw_net ip link set sw_port5 up
sudo docker exec -d leaf11 ip link set dev sw_port6 netns sw_net
sudo docker exec -d leaf11 ip netns exec sw_net sysctl net.ipv6.conf.sw_port6.disable_ipv6=1
sudo docker exec -d leaf11 ip netns exec sw_net ip link set sw_port6 up

sudo docker exec -d leaf12 ip netns add sw_net
sudo docker exec -d leaf12 ip link set dev sw_port0 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port0 up
sudo docker exec -d leaf12 ip link set dev sw_port5 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port5.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port5 up
sudo docker exec -d leaf12 ip link set dev sw_port6 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port6.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port6 up

sudo docker exec -d spine11 ip netns add sw_net
sudo docker exec -d spine11 ip link set dev sw_port0 netns sw_net
sudo docker exec -d spine11 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d spine11 ip netns exec sw_net ip link set sw_port0 up
sudo docker exec -d spine11 ip link set dev sw_port1 netns sw_net
sudo docker exec -d spine11 ip netns exec sw_net sysctl net.ipv6.conf.sw_port1.disable_ipv6=1
sudo docker exec -d spine11 ip netns exec sw_net ip link set sw_port1 up

sudo docker exec -d spine12 ip netns add sw_net
sudo docker exec -d spine12 ip link set dev sw_port0 netns sw_net
sudo docker exec -d spine12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d spine12 ip netns exec sw_net ip link set sw_port0 up
sudo docker exec -d spine12 ip link set dev sw_port1 netns sw_net
sudo docker exec -d spine12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port1.disable_ipv6=1
sudo docker exec -d spine12 ip netns exec sw_net ip link set sw_port1 up
echo "Configuring switches: done"

echo "Booting switches, please wait ~1 minute for switches to load: starting"
sudo docker exec -d leaf11 sh /sonic/scripts/startup.sh
sudo docker exec -d leaf12 sh /sonic/scripts/startup.sh
sudo docker exec -d spine11 sh /sonic/scripts/startup.sh
sudo docker exec -d spine12 sh /sonic/scripts/startup.sh
sleep 70
echo "Booting switches, please wait ~1 minute for switches to load: done"

echo "Fixing iptables firewall: starting"
sudo iptables -I FORWARD 1 -s 10.0.0.0/24 -d 10.0.0.0/24 -j ACCEPT
sudo iptables -I FORWARD 1 -s 192.168.0.0/16 -d 192.168.0.0/16 -j ACCEPT
echo "Fixing iptables firewall: done"
