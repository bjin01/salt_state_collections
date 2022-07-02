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
        return (
            False,
            'The crmsh execution module failed to load: the crm package'
            ' is not available.')

    if not use_crm:
        return (
            False,
            'crmsh is not installed.'
            ' package is not found.')
    
    #pacemaker_runnung = __salt__['service.status']("pacemaker.service")

    __salt__['crmsh.version'] = use_crm
    return __virtualname__

def _msl_status():
    hostname = socket.gethostname()
    ret = dict()
    ret["maintenance_approval"] = True
    ret['resources'] = []
    ret["node_comment"] = []
    ret['resource_comment'] = ""
    cluster_nodes = []
    master_slave_nodes = []
    dc = ""

    #First try to find the pacemaker cluster member nodes.
    out_crm_nodes = subprocess.Popen(['crm', 'node', 'server'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_crm_nodes.stdout.readline, b''):
        #create a list of found nodes.
        cluster_nodes.append(line.decode('utf-8').rstrip())

    #if no nodes found then output the message and set maintenance_approval to False and we end the func here, no need to continue.
    if len(cluster_nodes) == 0:
        ret['cluster nodes'] = "Error getting cluster nodes."
        ret["comment"] = "Failed to get cluster nodes."
        ret["maintenance_approval"] = False
        return ret

    #next we try to get resource status in xml format and do regex search.
    out_resources_xml = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )
    
    #here we try to find failed or unmanaged resources which are in maintenance mode
    seek_unmanaged_pattern = '.*managed=\"false\"'
    seek_resources_unmanaged_patterns = [
        '.*managed=\"false\"',
        '.*failed=\"true\"'
    ]

    for line in iter(out_resources_xml.stdout.readline, b''):
        #loop through the output and loop through the search pattern list
        for r in seek_resources_unmanaged_patterns:
            if re.search(r, line.decode('utf-8')):
                ret['resources'].append(line.decode('utf-8'))
                ret['resource_comment'] = "resources failed or in maintenance mode."
                ret["maintenance_approval"] = False
                
    #next try to identify which node is master and which node is slave in hana system replication scale-up scenario, it is easier to do parsing without xml in this case.
    out_master_slave_nodes = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1'],
                        stdout=subprocess.PIPE
                        )

    for line in iter(out_master_slave_nodes.stdout.readline, b''):
        master_node_pattern = '.*Master.*' + hostname
        slave_node_pattern = '.*Slave.*' + hostname

        if re.search(master_node_pattern, line.decode('utf-8')):
            master_slave_nodes.append(hostname)
            

        if re.search(slave_node_pattern, line.decode('utf-8')):
            master_slave_nodes.append(hostname)

    #now try to identify node status, if node is online but other status e.g. failed or unmanaged is true then we set the maintenance_approval to False as well. We don't allow continue patching if node status is not 100% ready prior patching states start.
    out_crm_node_status = subprocess.Popen(['crm_mon', '-1', '--exclude=all', '--include=nodes', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )

    ret["Nodes"] = {}

    
    for line in iter(out_crm_node_status.stdout.readline, b''):

        #Search if the current node is master or slave
        
        for c in cluster_nodes:
            #create a list of checking node status
            node_status_patterns = [
                '.*standby=\"true\"',
                '.*standby_onfail=\"true\"',
                '.*maintenance=\"true\"',
                '.*pending=\"true\"',
                '.*unclean=\"true\"',
                '.*shutdown=\"true\"',
                '.*expected_up=\"false\"'
            ]
            
            online_pattern = c.rstrip() + '.*online=\"true\".*'

            #if a node is offline then we also need to catch as other status will be false but online state is false
            offline_pattern = c.rstrip() + '.*online=\"false\".*'
            

            if re.search(online_pattern, line.decode('utf-8')):
                #print("--------found-------------{}---------".format(line.decode('utf-8').rstrip()))
                for n in node_status_patterns:
                    #print("#######{}----------{}".format(n, hostname))
                    if re.search(n, line.decode('utf-8')):
                        
                        print("#######{}----------{}".format(c, hostname))
                        ret["Nodes"][c] = "online {}".format(c)
                        ret["node_comment"].append("{} is online but {}.".format(c,n.lstrip(".*")))
                        ret["maintenance_approval"] = False
                    else:
                        ret["Nodes"][c] = "online"

            
            if re.search(offline_pattern, line.decode('utf-8')):
                #print("--------found-------------{}---------".format(line.decode('utf-8').rstrip()))
                ret["Nodes"][c] = "offline"
                ret["node_comment"].append("A cluster node is offline. {}".format(c))
                ret["maintenance_approval"] = False

    #here we need to find the dc node. With dc node found we can identify cluster state.
    out_crmadmin = subprocess.Popen(['crmadmin', '-D'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_crmadmin.stdout.readline, b''):
        if "Designated Controller is:" in line.decode('utf-8'):
            if len(cluster_nodes) > 0:
                
                for n in cluster_nodes:
                    if re.search(n, line.decode('utf-8').strip()):
                        dc = n
                        ret['Designated Controller'] = dc
            else:
                ret['Designated Controller'] = ""
                ret["comment"] = "Designated Controller could not be found."
                ret["maintenance_approval"] = False

    
    if len(dc):
        #if dc is found then we do cluster state query and match if cluster state is s_idle, if not then maintenance_approval will be set to False
        out_cluster_idle = subprocess.Popen(['crmadmin', '-q', '-S', dc.rstrip()],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )

        for line in iter(out_cluster_idle.stderr.readline, b''):
            #print("--------AAA---{}".format(line.decode('utf-8').strip()))
            ret['clusterstate'] = line.decode('utf-8').strip()
            if ret['clusterstate'] not in "S_IDLE":
                ret["dc_comment"] = "cluster state is not S_IDLE, wait until idle."
                ret["maintenance_approval"] = False
                #we end the func if cluster state is not s_idle. Then no need to further query the cluster.
                return ret

    #finally we query the hana system replication status.
    out1 = subprocess.Popen(['SAPHanaSR-showAttr'], 
                        stdout=subprocess.PIPE,
                        )
    
    if hostname in master_slave_nodes:

        #the secondary node if working correctly has a score value of 2 digits and must be 4:S and SOK
        sok_escaped = '.*[0-9]{2}.*4:S.*SOK'
        search_pattern_sok = "^{}".format(hostname) + sok_escaped
        #print("------------------------{}".format(search_pattern_sok))
        #the primary node if working properly has a score value of 10 digits and 4:P and PRIM
        prim_escaped = '.*[0-9]{10}.*4:P.*PRIM'
        search_pattern_prim = "^{}".format(hostname) + prim_escaped
        #and if SFAIL is found we must set status to maintenance_approval = False
        search_pattern_sfail = "^{}.*SFAIL".format(hostname)

        matches = 0
        
        for line in iter(out1.stdout.readline, b''):
            #print(".......{}".format(line.decode('utf-8').lower()))
           
            if re.search(search_pattern_sok, line.decode('utf-8')):
                ret['sr_status'] = "SOK"
                print("SOK")
                matches += 1
            if re.search(search_pattern_prim, line.decode('utf-8')):
                ret['sr_status'] = "PRIM"
                print("PRIM")
                matches += 1
            if re.search(search_pattern_sfail, line.decode('utf-8')):
                ret['sr_status'] = "SFAIL"
                ret["maintenance_approval"] = False
                matches += 2

        #the matches var is helping make sure each node in search pattern was found only one time if matches is higher then 1 then it means the node could be in prim and SOK or other wrong state, think about dual primary. So this is another insurance check.
        if matches != 1:
            ret['sr_status'] = "UNKNOWN"
            ret["comment"] = "system replication status unknown."
            ret["maintenance_approval"] = False
    else:
        #and if the node was not found in the list of master slave list then we put the state to none. In diskless SBD scenario we could have more than 2 nodes in a cluster.
        ret['sr_status'] = "None"
        ret["comment"] = "This host is not a HANA host."
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
        ret = dict()
        ret["comment"] = "pacemaker is not running"
        ret["maintenance_approval"] = False
        return ret
    else:
        #cmd = 'crm resource status msl_SAPHana_BJK_HDB00'
        ret = _msl_status()
        #print("#########super ret {}".format(ret))
        if not ret["maintenance_approval"]:
            __context__["retcode"] = 42
        return ret

def pacemaker():
    return __salt__['service.status']("pacemaker")
