from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path
import subprocess
import socket
import os
import re

__virtualname__ = 'bocrm'

CRMSH = 'crmsh'
CRM_COMMAND = '/usr/sbin/crm'
CRM_NEW_VERSION = '3.0.0'
CRM_CLUSTERSTATE = '/usr/sbin/cs_clusterstate'
LOGGER = logging.getLogger(__name__)

def __virtual__():
    '''
    Only load this module if crm package is installed
    '''
    if bool(salt.utils.path.which(CRM_COMMAND)):
        version = __salt__['pkg.version'](CRMSH)
        use_crm = __salt__['pkg.version_cmp'](
            version, CRM_NEW_VERSION) >= 0
        LOGGER.info('crmsh version: %s', version)
        LOGGER.info(
            '%s will be used', 'crm')

    else:
        #print("----------------------crm_command")
        return (

            False,
            'The crmsh execution module failed to load: the crm package'
            ' is not available.')

    if not use_crm or not bool(salt.utils.path.which(CRM_CLUSTERSTATE)):
        #print("----------------------errors")
        return (
            False,
            'Either crmsh and or ClusterTools2 is not installed.'
            ' package is not found.')
    
    #pacemaker_runnung = __salt__['service.status']("pacemaker.service")

    __salt__['crmsh.version'] = use_crm
    return __virtualname__

def _msl_status():
    ret = dict()
    cluster_nodes = []
    dc = ""
    # SAPHanaSR-showAttr | grep -E "^hana-1.*4:P:master1" | grep PRIM
    # crm_mon -1 | grep -i unmanaged
    # cs_clusterstate | grep -E "^Cluster state" | cut -d ":" -f 2
    # cs_clusterstate | grep -i "Stopped/FAILED" | cut -d ":" -f 2
    out_crm_nodes = subprocess.Popen(['crm', 'node', 'server'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_crm_nodes.stdout.readline, b''):
        cluster_nodes.append(line.decode('utf-8').rstrip())

    #print("-------------------------{}--------------".format(cluster_nodes))

    if len(cluster_nodes) == 0:
        ret['cluster nodes'] = "Error getting cluster nodes."
        return ret

    out_crm_node_status = subprocess.Popen(['crm_mon', '-1', '--exclude=Summary', '--exclude=resources', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )

    ret["Nodes"] = {}
    for line in iter(out_crm_node_status.stdout.readline, b''):
        
        for c in cluster_nodes:
            #online_pattern = re.escape('.*<node name=.*online="true"')
            online_pattern = c.rstrip() + '.*online=\"true\".*'
            offline_pattern = c.rstrip() + '.*online=\"false\".*'

            if re.search(online_pattern, line.decode('utf-8')):
                print("--------found-------------{}---------".format(line.decode('utf-8').rstrip()))
                ret["Nodes"][c] = "online"
            
            if re.search(offline_pattern, line.decode('utf-8')):
                print("--------found-------------{}---------".format(line.decode('utf-8').rstrip()))
                ret["Nodes"][c] = "offline"


    out_crmadmin = subprocess.Popen(['crmadmin', '-D'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_crmadmin.stdout.readline, b''):
        #print("--------###############{}".format(line.decode('utf-8')))
        if "Designated Controller is:" in line.decode('utf-8'):
            if len(cluster_nodes) > 0:
                
                for n in cluster_nodes:
                    #print("--------###############{}".format(n))
                    if re.search(n, line.decode('utf-8').strip()):
                        dc = n
                        ret['Designated Controller'] = dc
            else:
                ret['Designated Controller'] = "" 

    
    if len(dc):
        #print("get here -------------------------{}".format(dc))
        out_cluster_idle = subprocess.Popen(['crmadmin', '-q', '-S', dc.rstrip()],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )
        #print("--------------{}-----------------".format(out_cluster_idle))
        for line in iter(out_cluster_idle.stderr.readline, b''):
            #print("--------AAA---{}".format(line.decode('utf-8').strip()))
            ret['clusterstate'] = line.decode('utf-8').strip()


    # crm_mon -1 --exclude="Summary" --exclude="nodes" --exclude="resources" --include="nodes" -X | grep -E "<node name=\"hana-2\".* online"
    # crmadmin -q -S hana-1
    # crmadmin -q -S hana-2 2>&1 >/dev/null

    hostname = socket.gethostname()

    out1 = subprocess.Popen(['SAPHanaSR-showAttr'], 
                        stdout=subprocess.PIPE,
                        )


    #| grep -E ^hana-.*4:.*SOK|PRIM.*
    sok_escaped = '.*[0-9]{2}.*4:S.*SOK'
    search_pattern_sok = "^{}".format(hostname) + sok_escaped
    #print("------------------------{}".format(search_pattern_sok))
    prim_escaped = '.*[0-9]{10}.*4:P.*PRIM'
    search_pattern_prim = "^{}".format(hostname) + prim_escaped
    search_pattern_sfail = "^{}.*SFAIL".format(hostname)

    matches = 0
    for line in iter(out1.stdout.readline, b''):
        if re.search("failed", line.decode('utf-8').lower()):
            ret['resources'] = "Found failed resources."
        if re.search("unmanaged", line.decode('utf-8').lower()):
            ret['resources'] = "Found resources in maintenance mode."
        if re.search(search_pattern_sok, line.decode('utf-8')):
            ret['sr_status'] = "SOK"
            matches += 1
        if re.search(search_pattern_prim, line.decode('utf-8')):
            ret['sr_status'] = "PRIM"
            matches += 1
        if re.search(search_pattern_sfail, line.decode('utf-8')):
            ret['sr_status'] = "SFAIL"
            matches += 1


    if matches != 1:
        ret['sr_status'] = "UNKNOWN"
    
    return ret

def sync_status():
    '''
    Show cluster status. The status is displayed by crm_mon. Supply additional
    arguments for more information or different format.

    CLI Example:

    .. code-block:: bash

        salt '*' bocrm.sync_status
    '''
    if not bool(__salt__['service.status']("pacemaker")):
        return "pacemaker is not running"
    else:
        #cmd = 'crm resource status msl_SAPHana_BJK_HDB00'
        ret = _msl_status()
        return ret

def pacemaker():
    return __salt__['service.status']("pacemaker")
