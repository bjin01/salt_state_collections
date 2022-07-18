from __future__ import absolute_import, print_function, unicode_literals

# Import python libs
import atexit
import logging
import socket
import salt.client
import time
import subprocess
import re

# Import third party libs
from salt.ext import six

from datetime import datetime,  timedelta

log = logging.getLogger(__name__)


def __virtual__():
    return True

def set(hana_nodes):
    #print("----------------------data {}".format(hana_nodes['cluster_nodes']))
    
    minion_list = []
    roles = ['hana_primary', 'hana_secondary', 'diskless_node']

    #salt-key --list="acc"
    out_saltkey = subprocess.Popen(['salt-key', '--list=acc'],
                        stdout=subprocess.PIPE
                        )

    for line in iter(out_saltkey.stdout.readline, b''):
        for i in hana_nodes['cluster_nodes']:
            if re.search(i, line.decode('utf-8')):
                minion_list.append(line.decode('utf-8').strip())
    
    if len(minion_list) != 0:
        
        for m in minion_list:
            #ret_grains_set = __salt__['salt.execute'](m, 'grains.append', ('hana_info', hana_nodes))
            ret_grains_set = __salt__['salt.execute'](m, 'grains.set', ('hana_info:clusternodes', hana_nodes['cluster_nodes'], 'force=True'))

            for r in roles:
                if r in hana_nodes:
                    grains_key = "hana_info:{}".format(r)
                    ret_grains_set = __salt__['salt.execute'](m, 'grains.set', (grains_key, hana_nodes[r], 'force=True'))
            print("rrrrrrrrrrrrrr roles result {}".format(ret_grains_set))
            #__salt__['salt.execute'](m, 'grains.set', ({'hana_info': hana_nodes}))

    return minion_list