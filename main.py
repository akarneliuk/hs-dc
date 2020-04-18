#!/usr/bin/env python

# Modules
import yaml
import random
import networkx


# Variables
path_inventory = 'inventory/build.yaml'
parh_resources = 'inventory/resources.yaml'
path_output = 'topology/autogen.gv'

colours = ['deepskyblue', 'gold', 'lightgrey', 'orangered', 'cyan', 'red', 'magenta', 'coral']
chosen_colours = {}

primitives = {}

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


# Body
if __name__ == '__main__':
    inventory = yaml_dict(path_inventory)
    resources = yaml_dict(parh_resources)

    DG = networkx.Graph(label='Data Centre')

    # Adding the devices
    dev_id = 0

    for dev_group, dev_list in inventory.items():
        for elem in dev_list:
            DG.add_node(elem['name'], pod=elem['pod'], 
                        dev_type=elem['dev_type'],
                        style='filled', fillcolor=set_colour(elem, dev_group))

            if dev_group in ['aggs', 'spines', 'leafs']:
                DG.nodes[elem['name']]['bgp_asn'] = resources['bgp']['asn'] + dev_id
                DG.nodes[elem['name']]['label'] = f'{elem["name"]}\n{resources["bgp"]["asn"] + dev_id}'

                dev_id += 1

    # Adding the links
    if_id = 0

    for le in inventory['leafs']:
        for ho in inventory['hosts']:
           if ho['connection_point'] == le['name']:
               DG.add_node(f'iface-{if_id}', label='Eth', dev_type='port')
               DG.add_edge(le['name'], f'iface-{if_id}', phy='port', color='coral')

               DG.add_node(f'iface-{if_id + 1}', label='Eth', dev_type='port')
               DG.add_edge(ho['name'], f'iface-{if_id + 1}', phy='port', color='coral')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='customer', color='indigo')

               if_id += 2

    for sp in inventory['spines']:
        for le in inventory['leafs']:
           if sp['pod'] == le['pod']:
               DG.add_node(f'iface-{if_id}', label='Eth', dev_type='port')
               DG.add_edge(sp['name'], f'iface-{if_id}', phy='port', color='coral')

               DG.add_node(f'iface-{if_id + 1}', label='Eth', dev_type='port')
               DG.add_edge(le['name'], f'iface-{if_id + 1}', phy='port', color='coral')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='indigo')

               if_id += 2

    for ag in inventory['aggs']:
        for sp in inventory['spines']:
               DG.add_node(f'iface-{if_id}', label='Eth', dev_type='port')
               DG.add_edge(ag['name'], f'iface-{if_id}', phy='port', color='coral')

               DG.add_node(f'iface-{if_id + 1}', label='Eth', dev_type='port')
               DG.add_edge(sp['name'], f'iface-{if_id + 1}', phy='port', color='coral')

               DG.add_edge(f'iface-{if_id}', f'iface-{if_id + 1}', phy='wire', role='dc', color='indigo')

               if_id += 2

    # Print the graph
    VG = networkx.drawing.nx_agraph.to_agraph(DG)

    with open(path_output, 'w') as file:
        file.write(str(VG))

    VG.layout('dot')
    VG.draw(f'{path_output}.png')

