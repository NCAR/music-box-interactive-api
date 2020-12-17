from interactive.tools import *


def get_valid_runs():
    index = open_json('log_config.json')['history']
    li = []
    for i in index:
        if index[i] == 'done':
            li.append(i)
    return li


