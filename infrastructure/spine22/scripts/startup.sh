[ -d /etc/sonic ] || mkdir -p /etc/sonic

SYSTEM_MAC_ADDRESS=00:dc:5e:01:01:09
ip link add eth0 addr $SYSTEM_MAC_ADDRESS type dummy

if [ -f /etc/sonic/config_db.json ]; then
    sonic-cfggen -j /etc/sonic/config_db.json -j /sonic/scripts/vlan_config.json --print-data > /tmp/config_db.json
    mv /tmp/config_db.json /etc/sonic/config_db.json
else
    sonic-cfggen -j /sonic/etc/config_db/vlan_config.json --print-data > /etc/sonic/config_db.json
fi

#chmod +x /usr/bin/config_bm.sh # TODO: remove this line
cp -f /sonic/etc/swss/config.d/00-copp.config.json /etc/swss/config.d/default_config.json
cp -rf /sonic/etc/quagga /etc/
ip netns exec sw_net ip link set dev sw_port0 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port1 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port2 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port3 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port4 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port5 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port6 addr $SYSTEM_MAC_ADDRESS
ip netns exec sw_net ip link set dev sw_port7 addr $SYSTEM_MAC_ADDRESS
supervisord