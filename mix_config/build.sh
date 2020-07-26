#/usr/bin/env bash

K_FABRIC1='srlinux:19.11.7-75'
K_FABRIC2='docker-sonic-p4:latest'
K_HOST='ubuntu:14.04'

# Step 1
echo "$(date): Launching Docker // starting..."

sudo systemctl start docker.service

echo "$(date): Launching Docker // done"

# Step 2
echo "$(date): Creating the containers // starting..."

FABRIC=('leaf11' 'leaf12' 'spine11' 'spine12' 'host11' 'host12')
for CENTRY in ${FABRIC[@]}; do

  # Bulding Nokia SRL network function
  if [[ ${CENTRY} == 'leaf11' || ${CENTRY} == 'spine11' ]]; then
    sudo docker run --privileged \
      --user root --env SRLINUX=1 \
      --name ${CENTRY} --hostname ${CENTRY} -it -d \
      -v $PWD/shared/license.key:/opt/srlinux/etc/license.key:ro \
      -v $PWD/${CENTRY}/config.json:/etc/opt/srlinux/config.json:rw \
      -v $PWD/${CENTRY}/srlinux.conf:/home/admin/.srlinux.conf:rw \
      -v $PWD/${CENTRY}/tls/:/etc/opt/srlinux/tls/:rw \
      -v $PWD/${CENTRY}/checkpoint/:/etc/opt/srlinux/checkpoint/:rw \
      ${K_FABRIC1} \
      bash -c 'sudo /opt/srlinux/bin/createuser.sh && /opt/srlinux/bin/sr_facls.sh && /opt/srlinux/bin/sr_linux'

  # Bulding Microsoft Azure SONiC network function
  elif [[ ${CENTRY} == 'leaf12' || ${CENTRY} == 'spine12' ]]; then
    sudo docker run --net=none --privileged \
      --entrypoint /bin/bash --name ${CENTRY} -it -d \
      -v $PWD/${CENTRY}:/sonic \
      ${K_FABRIC2}

  # Building Ubuntu host
  else
    sudo docker run --net=none --privileged \
      --entrypoint /bin/bash \
      --name ${CENTRY} --hostname ${CENTRY} -it -d ${K_HOST}

  fi

  sleep 5

  PID=$(sudo docker inspect --format '{{ .State.Pid }}' ${CENTRY})

  sudo ip netns attach ns_${CENTRY} ${PID}
done

echo "$(date): Creating the containers // done"

# Step 3
echo "$(date): Creating the network connectivity // starting..."

# SONiC-specific step
SONICS=('leaf12' 'spine12')
for C_S in ${SONICS[@]}; do
  sudo docker exec -d ${C_S} ip netns add sw_net
done

# Leaf11 - Spine11
sudo ip link add leaf11_1 type veth peer name spine11_1
sudo ip link set leaf11_1 netns ns_leaf11
sudo ip link set spine11_1 netns ns_spine11
sudo ip netns exec ns_leaf11 ip link set leaf11_1 name e1-1
sudo ip netns exec ns_spine11 ip link set spine11_1 name e1-1
sudo ip netns exec ns_leaf11 ip link set e1-1 up
sudo ip netns exec ns_spine11 ip link set e1-1 up

# Leaf12 - Spine11
sudo ip link add spine11_2 type veth peer name leaf12_1
sudo ip link set spine11_2 netns ns_spine11
sudo ip link set leaf12_1 netns ns_leaf12
sudo ip netns exec ns_spine11 ip link set spine11_2 name e1-2
sudo ip netns exec ns_leaf12 ip link set leaf12_1 name sw_port0
sudo ip netns exec ns_spine11 ip link set e1-2 up
sudo docker exec -d leaf12 ip link set dev sw_port0 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port0 up

# Leaf11 - Spine12
sudo ip link add leaf11_2 type veth peer name spine12_1
sudo ip link set leaf11_2 netns ns_leaf11
sudo ip link set spine12_1 netns ns_spine12
sudo ip netns exec ns_leaf11 ip link set leaf11_2 name e1-2
sudo ip netns exec ns_spine12 ip link set spine12_1 name sw_port0
sudo ip netns exec ns_leaf11 ip link set e1-2 up
sudo docker exec -d spine12 ip link set dev sw_port0 netns sw_net
sudo docker exec -d spine12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port0.disable_ipv6=1
sudo docker exec -d spine12 ip netns exec sw_net ip link set sw_port0 up

# Leaf12 - Spine12
sudo ip link add leaf12_2 type veth peer name spine12_2
sudo ip link set leaf12_2 netns ns_leaf12
sudo ip link set spine12_2 netns ns_spine12
sudo ip netns exec ns_leaf12 ip link set leaf12_2 name sw_port1
sudo ip netns exec ns_spine12 ip link set spine12_2 name sw_port1
sudo docker exec -d leaf12 ip link set dev sw_port1 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port1.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port1 up
sudo docker exec -d spine12 ip link set dev sw_port1 netns sw_net
sudo docker exec -d spine12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port1.disable_ipv6=1
sudo docker exec -d spine12 ip netns exec sw_net ip link set sw_port1 up

# Leaf11 - Host11
sudo ip link add leaf11_3 type veth peer name host11_1
sudo ip link set leaf11_3 netns ns_leaf11
sudo ip link set host11_1 netns ns_host11
sudo ip netns exec ns_leaf11 ip link set leaf11_3 name e1-3
sudo ip netns exec ns_host11 ip link set host11_1 name eth1
sudo ip netns exec ns_leaf11 ip link set e1-3 up
sudo ip netns exec ns_host11 ip link set eth1 up

# Leaf12 - Host12
sudo ip link add leaf12_3 type veth peer name host12_1
sudo ip link set leaf12_3 netns ns_leaf12
sudo ip link set host12_1 netns ns_host12
sudo ip netns exec ns_leaf12 ip link set leaf12_3 name sw_port5
sudo ip netns exec ns_host12 ip link set host12_1 name eth1
sudo docker exec -d leaf12 ip link set dev sw_port5 netns sw_net
sudo docker exec -d leaf12 ip netns exec sw_net sysctl net.ipv6.conf.sw_port5.disable_ipv6=1
sudo docker exec -d leaf12 ip netns exec sw_net ip link set sw_port5 up
sudo ip netns exec ns_host12 ip link set eth1 up
echo "$(date): Creating the network connectivity // done"

echo "$(date): Configuring SONiC // starting..."
SONICS=('leaf12' 'spine12')
for C_S in ${SONICS[@]}; do
  sudo docker exec -d ${C_S} sh /sonic/scripts/startup.sh
done
echo "$(date): Configuring SONiC // done"

echo "$(date): Configuring hosts // starting..."
sudo docker container exec -d host11 sysctl net.ipv6.conf.eth1.disable_ipv6=1
sudo docker container exec -d host12 sysctl net.ipv6.conf.eth1.disable_ipv6=1

sudo docker container exec -d host11 ifconfig eth1 192.168.1.2/24 mtu 1400
sudo docker container exec -d host11 ip route replace default via 192.168.1.1

sudo docker container exec -d host12 ifconfig eth1 192.168.2.2/24 mtu 1400
sudo docker container exec -d host12 ip route replace default via 192.168.2.1
echo "$(date): Configuring hosts // starting..."

echo "$(date): Fixing iptables firewall // starting..."
sudo iptables -I FORWARD 1 -s 10.0.0.0/24 -d 10.0.0.0/24 -j ACCEPT
sudo iptables -I FORWARD 1 -s 192.168.0.0/16 -d 192.168.0.0/16 -j ACCEPT
echo "$(date): Fixing iptables firewall // done"

