#!/usr/bin/env python

# Modules
import yaml
import random
import networkx
import netaddr


# Variables
path_inventory = 'inventory/build.yaml'
parh_resources = 'inventory/resources.yaml'
path_output = 'topology/autogen.gv'
path_primitives = 'primitives'

colours = ['deepskyblue', 'gold', 'lightgrey', 'orangered', 'cyan', 'red', 'magenta', 'coral']
chosen_colours = {}

list_of_primitives = []
if_count = {}


# User-defined functions
def yaml_dict(file_path):
    with open(file_path, 'r') as temp_file:
        temp_dict = yaml.load(temp_file.read(), Loader=yaml.Loader)
        return temp_dict


def set_colour(dev_info, dev_role):
    available_colours = len(colours)
    colour_choice = 'black'

    if dev_role == 'aggs':
        colour_choice = colours.pop(random.randrange(available_colours))
        chosen_colours[dev_info['name']] = colour_choice

    elif dev_info['pod']:
        if f'pod_{dev_info["pod"]}' in chosen_colours:
            colour_choice = chosen_colours[f'pod_{dev_info["pod"]}']

        else:
            colour_choice = colours.pop(random.randrange(available_colours))
            chosen_colours[f'pod_{dev_info["pod"]}'] = colour_choice

    return colour_choice


def set_rank(build_res, list_nodes):
    if not list_nodes[1]:
        r = build_res[f'{list_nodes[0]}']

    else:
        r = build_res[f'if_{list_nodes[0]}_{list_nodes[1]}']

    return r


# Body
if __name__ == '__main__':
    # Loading resources
    inventory = yaml_dict(path_inventory)
    resources = yaml_dict(parh_resources)

    # Creating graph
    DG = networkx.Graph(label='Data Centre', rankdir='TD')

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
                DG.nodes[elem['name']]['loopback'] = ip_addr[dev_id]

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
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[le["name"]]["dev_role"], DG.nodes[ho["name"]]["dev_role"]]))
               DG.add_edge(le['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[ho["dev_type"]]["iface"]["name"]}{if_count[ho["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31', 
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31', 
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
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31', 
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[sp["name"]]["dev_role"], DG.nodes[le["name"]]["dev_role"]]))
               DG.add_edge(sp['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[le["dev_type"]]["iface"]["name"]}{if_count[le["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31', 
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[le["name"]]["dev_role"], DG.nodes[sp["name"]]["dev_role"]]))
               DG.add_edge(le['name'], f'iface-{if_id + 1}', phy='port', color='black')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='coral', linux_bridge=f'hs_br_{if_id}')

               if_id += 2
               if_count[sp["name"]] += 1
               if_count[le["name"]] += 1

    for ag in inventory['aggs']:
        for sp in inventory['spines']:
               DG.add_node(f'iface-{if_id}', label=f'{primitives[ag["dev_type"]]["iface"]["name"]}{if_count[ag["name"]]}\n{str(ip_addr[if_id]).split("/")[0]}/31', 
                           ipv4=f'{str(ip_addr[if_id]).split("/")[0]}/31',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[ag["name"]]["dev_role"], DG.nodes[sp["name"]]["dev_role"]]))
               DG.add_edge(ag['name'], f'iface-{if_id}', phy='port', color='black')

               DG.add_node(f'iface-{if_id + 1}', label=f'{primitives[sp["dev_type"]]["iface"]["name"]}{if_count[sp["name"]]}\n{str(ip_addr[if_id + 1]).split("/")[0]}/31', 
                           ipv4=f'{str(ip_addr[if_id + 1]).split("/")[0]}/31',
                           dev_type='port', rank=set_rank(resources['ranks'], [DG.nodes[sp["name"]]["dev_role"], DG.nodes[ag["name"]]["dev_role"]]))
               DG.add_edge(sp['name'], f'iface-{if_id + 1}', phy='port', color='black')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='coral', linux_bridge=f'hs_br_{if_id}')

               if_id += 2
               if_count[ag["name"]] += 1
               if_count[sp["name"]] += 1

    # Visualising the graph
    VG = networkx.drawing.nx_agraph.to_agraph(DG)

    with open(path_output, 'w') as file:
        file.write(str(VG))

    VG.layout('dot')
    VG.draw(f'{path_output}.png')

