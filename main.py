#!/usr/bin/env python

# Modules
from graphviz import Graph
import yaml


# Variables
path_inventory = 'inventory/build.yaml'
path_output = 'topology/autogen.gv'


# User-defined functions
def yaml_dict(file_path):
    with open(file_path, 'r') as temp_file:
        temp_dict = yaml.load(temp_file.read(), Loader=yaml.Loader)
        return temp_dict


# Body
if __name__ == '__main__':
    inventory = yaml_dict(path_inventory)

    dot = Graph(comment='Data Centre', format='png', node_attr={'color': 'deepskyblue1', 'style': 'filled'})

    # Adding the devices
    for dev_role, dev_list in inventory.items():
        for elem in dev_list:
            dot.node(elem['name'], pod=elem['pod'], dev_type=elem['dev_type'])

    # Adding the nodes
    for le in inventory['leafs']:
        for ho in inventory['hosts']:
           if ho['connection_point'] == le['name']:
               dot.edge(le['name'], ho['name'], type='link_customer')

    for sp in inventory['spines']:
        for le in inventory['leafs']:
           if sp['pod'] == le['pod']:
               dot.edge(sp['name'], le['name'], type='link_dc')

    for ag in inventory['aggs']:
        for sp in inventory['spines']:
            dot.edge(ag['name'], sp['name'], type='link_dc')

    with open(path_output, 'w') as file:
        file.write(dot.source)

    dot.render(path_output, view=True)
