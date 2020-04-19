#!/usr/bin/env python

# Modules
import yaml
import random


# Variables
colours = ['deepskyblue', 'gold', 'lightgrey', 'orangered', 'cyan', 'red', 'magenta', 'coral']
chosen_colours = {}

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
