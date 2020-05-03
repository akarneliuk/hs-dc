#!/usr/bin/env python

# Modules
from bin.localfunctions import *
import networkx
import netaddr
import os
import re
import jinja2
import docker


# Variables
path_inventory = 'inventory/build.yaml'
path_resources = 'inventory/resources.yaml'
path_output = 'topology/autogen.gv'
path_primitives = 'primitives'
path_infra = 'infrastructure'

list_of_primitives = []
if_count = {}


# Body
if __name__ == '__main__':
    # Loading resources
    inventory = yaml_dict(path_inventory)
    resources = yaml_dict(path_resources)

    # Creating graph
    DG = networkx.Graph(label='Data Centre')

    # Adding the devices to the graph
    dev_id = 0
    ip_addr = netaddr.IPNetwork(resources['ip']['loop'])

    for dev_group, dev_list in inventory.items():
        for elem in dev_list:
            DG.add_node(elem['name'], pod=elem['pod'],
                        dev_type=elem['dev_type'], dev_role=dev_group,
                        style='filled', fillcolor=set_colour(elem, dev_group),
                        rank=set_rank(resources['ranks'], [dev_group, None]))

            if dev_group in ['aggs', 'spines', 'leafs']:
                DG.nodes[elem['name']]['bgp_asn'] = resources['bgp']['asn'] + dev_id
                DG.nodes[elem['name']]['label'] = f'{elem["name"]}\n{resources["bgp"]["asn"] + dev_id}\n{ip_addr[dev_id]}'
                DG.nodes[elem['name']]['loopback'] = str(ip_addr[dev_id])
                if (len(format(dev_id, 'x'))) < 2:
                    DG.nodes[elem['name']]['mac'] = f'00:dc:5e:01:01:0{format(dev_id, "x")}'

                elif (len(format(dev_id, 'x'))) < 3:
                    DG.nodes[elem['name']]['mac'] = f'00:dc:5e:01:01:{format(dev_id, "x")}'

                if DG.nodes[elem['name']]['dev_type'] == 'microsoft-sonic':
                    DG.nodes[elem['name']]['vlan_base'] = dev_id*10

                dev_id += 1

            list_of_primitives.append(elem['dev_type']) if elem['dev_type'] not in list_of_primitives else None
            if_count[elem['name']] = 0

    # Loading the primitives
    primitives = {}
    for primitve_entry in list_of_primitives:
        primitives[primitve_entry] = yaml_dict(f'{path_primitives}/{primitve_entry}.yaml')

    # Adding the links to the graph
    if_id = 0
    ip_addr = netaddr.IPNetwork(resources['ip']['customer'])

    for le in inventory['leafs']:
        for ho in inventory['hosts']:
           if ho['connection_point'] == le['name']:
               DG.add_node(f'iface-{if_id}', label=f'{primitives[le["dev_type"]]["iface"]["name"]}{if_count[le["name"]]}\n{str(ip_addr[if_id]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31', dev_name=f'{primitives[le["dev_type"]]["iface"]["name"]}{if_count[le["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[le["name"]]["dev_role"], DG.nodes[ho["name"]]["dev_role"]]))
               DG.add_edge(le['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[ho["dev_type"]]["iface"]["name"]}{if_count[ho["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31', dev_name=f'{primitives[ho["dev_type"]]["iface"]["name"]}{if_count[ho["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[ho["name"]]["dev_role"], DG.nodes[le["name"]]["dev_role"]]))
               DG.add_edge(ho['name'], f'iface-{if_id + 1}', phy='port', color='black')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='customer', color='coral', linux_bridge=f'hs_br_{if_id}')

               if_id += 2
               if_count[le["name"]] += 1
               if_count[ho["name"]] += 1

    ip_addr = netaddr.IPNetwork(resources['ip']['dc'])

    for sp in inventory['spines']:
        for le in inventory['leafs']:
           if sp['pod'] == le['pod']:
               DG.add_node(f'iface-{if_id}', label=f'{primitives[sp["dev_type"]]["iface"]["name"]}{if_count[sp["name"]]}\n{str(ip_addr[if_id]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31', dev_name=f'{primitives[sp["dev_type"]]["iface"]["name"]}{if_count[sp["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[sp["name"]]["dev_role"], DG.nodes[le["name"]]["dev_role"]]))
               DG.add_edge(sp['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[le["dev_type"]]["iface"]["name"]}{if_count[le["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31', dev_name=f'{primitives[le["dev_type"]]["iface"]["name"]}{if_count[le["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[le["name"]]["dev_role"], DG.nodes[sp["name"]]["dev_role"]]))
               DG.add_edge(le['name'], f'iface-{if_id + 1}', phy='port', color='black')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='coral', linux_bridge=f'hs_br_{if_id}')

               if_id += 2
               if_count[sp["name"]] += 1
               if_count[le["name"]] += 1

    for ag in inventory['aggs']:
        for sp in inventory['spines']:
               DG.add_node(f'iface-{if_id}', label=f'{primitives[ag["dev_type"]]["iface"]["name"]}{if_count[ag["name"]]}\n{str(ip_addr[if_id]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31', dev_name=f'{primitives[ag["dev_type"]]["iface"]["name"]}{if_count[ag["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[ag["name"]]["dev_role"], DG.nodes[sp["name"]]["dev_role"]]))
               DG.add_edge(ag['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[sp["dev_type"]]["iface"]["name"]}{if_count[sp["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31',
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31', dev_name=f'{primitives[sp["dev_type"]]["iface"]["name"]}{if_count[sp["name"]]}',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[sp["name"]]["dev_role"], DG.nodes[ag["name"]]["dev_role"]]))
               DG.add_edge(sp['name'], f'iface-{if_id + 1}', phy='port', color='black')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='coral', linux_bridge=f'hs_br_{if_id}')

               if_id += 2
               if_count[ag["name"]] += 1
               if_count[sp["name"]] += 1

    # Building the lab topology
    for node_entry in DG.nodes.data():
        if node_entry[1]['dev_type'] != 'port':
            templating_data = {}
            templating_data['hostname'] = node_entry[0]
            templating_data['general'] = node_entry[1]


            # Creating list of the interfaces
            templating_data['interfaces'] = []
            for port_entry in DG.adj[node_entry[0]]:
                port_dict = DG.nodes[port_entry]

                if node_entry[1]['dev_type'] == 'microsoft-sonic':
                    port_id = 10 + int(re.sub(f'{primitives[node_entry[1]["dev_type"]]["iface"]["name"]}','', port_dict['label'].split('\n')[0]))
                    port_dict['vlan'] = port_id

                for connected_item in DG.adj[port_entry]:
                    for abc in DG.adj[connected_item].items():
                        if abc[1]['phy'] == 'wire':
                            if abc[1]['role'] == 'customer':
                                port_dict['customer'] = True

                            elif abc[1]['role'] == 'dc':
                                port_dict['customer'] = False

                                for nested_abc in DG.adj[abc[0]].items():
                                    if nested_abc[1]['phy'] == 'wire':
                                        port_dict['bgp_peer'] = DG.nodes[nested_abc[0]]['ipv4'].split('/')[0]

                                        for nested_nested_abc in DG.adj[nested_abc[0]].items():
                                            if nested_nested_abc[1]['phy'] == 'port':
                                                port_dict['bgp_asn'] = DG.nodes[nested_nested_abc[0]]['bgp_asn']

                templating_data['interfaces'].append(port_dict)

            # Templating the configuration files
            if not os.path.exists(f'{path_infra}/{node_entry[0]}'):
                os.makedirs(f'{path_infra}/{node_entry[0]}')

            if primitives[node_entry[1]['dev_type']]['templates']:
                for temp_entry in primitives[node_entry[1]['dev_type']]['templates']:
                    if not os.path.exists(f'{path_infra}/{node_entry[0]}/{temp_entry["destination"]}'):
                        os.makedirs(f'{path_infra}/{node_entry[0]}/{temp_entry["destination"]}')

                    if temp_entry['type'] == 'static':
                        os.popen(f'cp primitives/templates/{node_entry[1]["dev_type"]}/{temp_entry["source"]} {path_infra}/{node_entry[0]}/{temp_entry["destination"]}/{temp_entry["source"]}')

                    elif temp_entry['type'] == 'dynamic':
                        with open(f'{path_primitives}/templates/{node_entry[1]["dev_type"]}/{temp_entry["source"]}', 'r') as template_file:
                            template = jinja2.Template(template_file.read())

                        with open(f'{path_infra}/{node_entry[0]}/{temp_entry["destination"]}/{re.sub(".j2", "", temp_entry["source"])}', 'w') as target_config:
                            target_config.write(template.render(temp_data=templating_data))

    # Launching the emulated network
    print('Launching the network emulation.')
    docker_client = docker.from_env()
    temp_current_path = os.getcwd()

    for node_entry in DG.nodes.data():
        if 'dev_role' in node_entry[1]:
            if primitives[node_entry[1]['dev_type']]['image']['type'] == 'docker':
                print(f'Creating the Docker container with {node_entry[0]}...')

                if node_entry[1]['dev_role'] != 'host':
                    container_node = docker_client.containers.run(image=primitives[node_entry[1]['dev_type']]['image']['name'],
                                                                  detach=True,
                                                                  privileged=True,
                                                                  tty=True,
                                                                  stdin_open=True,
                                                                  network_mode='none',
                                                                  name=node_entry[0],
                                                                  entrypoint='/bin/bash',
                                                                  volumes={f'{temp_current_path}/{path_infra}/{node_entry[0]}': {'bind': '/sonic', 'mode': 'rw'}})

                else:
                    container_node = docker_client.containers.run(image=primitives[node_entry[1]['dev_type']]['image']['name'],
                                                                  detach=True,
                                                                  privileged=True,
                                                                  tty=True,
                                                                  stdin_open=True,
                                                                  network_mode='none',
                                                                  name=node_entry[0],
                                                                  entrypoint='/bin/bash')

                docker_llapi = docker.APIClient(base_url='unix://var/run/docker.sock')
                node_entry[1]['pid'] = docker_llapi.inspect_container(node_entry[0])['State']['Pid']

    # Connecting containers
    veth_id = 0

    for node_entry in DG.nodes.data():
        if 'dev_role' in node_entry[1]:
            print(f'Building connections for {node_entry[0]} ...')
            container_node = docker_client.containers.get(node_entry[0])
            container_node.exec_run('ip netns add sw_net', detach=True)

            for iface_id in DG.adj[node_entry[0]]:
                for link_data in DG.adj[iface_id].items():
                    if link_data[1]['phy'] != 'port':
                        os.system(f'sudo brctl addbr {link_data[1]["linux_bridge"]}')
                        os.system(f'sudo ip link set {link_data[1]["linux_bridge"]} up')

                        if node_entry[1]['dev_type'] == 'microsoft-sonic':
                            os.system(f'sudo ip link add sw_port{DG.nodes[iface_id]["vlan"] - 10} type veth')

                        else:
                            os.system(f'sudo ip link add {DG.nodes[iface_id]["dev_name"]} type veth')

                        os.system(f'sudo ip link set veth{veth_id} up')
                        os.system(f'sudo brctl addif {link_data[1]["linux_bridge"]} veth{veth_id}')

                        if node_entry[1]['dev_type'] == 'microsoft-sonic':
                            os.system(f'sudo ip link set netns {DG.nodes[node_entry[0]]["pid"]} dev sw_port{DG.nodes[iface_id]["vlan"] - 10}')

                        else:
                            os.system(f'sudo ip link set netns {DG.nodes[node_entry[0]]["pid"]} dev {DG.nodes[iface_id]["dev_name"]}')

                        if node_entry[1]['dev_type'] == 'microsoft-sonic':
                            container_node.exec_run(f'ip link set dev sw_port{DG.nodes[iface_id]["vlan"] - 10} netns sw_net', detach=True)
                            container_node.exec_run(f'ip netns exec sw_net sysctl net.ipv6.conf.sw_port{DG.nodes[iface_id]["vlan"] - 10}.disable_ipv6=1', detach=True)
                            container_node.exec_run(f'ip netns exec sw_net ip link set sw_port{DG.nodes[iface_id]["vlan"] - 10} up', detach=True)

                        elif node_entry[1]['dev_type'] == 'ubuntu' and node_entry[1]['dev_role'] == 'hosts':
                            container_node.exec_run(f'sysctl net.ipv6.conf.{DG.nodes[iface_id]["dev_name"]}.disable_ipv6=1', detach=True)
                            container_node.exec_run(f'ifconfig {DG.nodes[iface_id]["dev_name"]} {DG.nodes[iface_id]["ipv4"]} mtu 1400', detach=True)
                            container_node.exec_run(f'ip route replace default via {DG.nodes[link_data[0]]["ipv4"].split("/")[0]}', detach=True)

                        veth_id += 1

            if node_entry[1]['dev_type'] == 'microsoft-sonic':
                container_node.exec_run('sh /sonic/scripts/startup.sh', detach=True)
                print('sh /sonic/scripts/startup.sh')

    # Modigyin FW rules
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["loop"]} -d {resources["ip"]["loop"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["loop"]} -d {resources["ip"]["customer"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["loop"]} -d {resources["ip"]["dc"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["dc"]} -d {resources["ip"]["dc"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["dc"]} -d {resources["ip"]["loop"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["dc"]} -d {resources["ip"]["customer"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["customer"]} -d {resources["ip"]["customer"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["customer"]} -d {resources["ip"]["loop"]} -j ACCEPT')
    os.system(f'sudo iptables -I FORWARD 1 -s {resources["ip"]["customer"]} -d {resources["ip"]["dc"]} -j ACCEPT')

    # Visualising the graph
    VG = networkx.drawing.nx_agraph.to_agraph(DG)

    with open(path_output, 'w') as file:
        file.write(str(VG))

    VG.layout('dot')
    VG.draw(f'{path_output}.png')
