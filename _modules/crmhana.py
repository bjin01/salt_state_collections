from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path
import subprocess
import socket
import os
import re
import time

__virtualname__ = 'bocrm'

CRMSH = 'crmsh'
CRM_COMMAND = '/usr/sbin/crm'
CRM_NEW_VERSION = '3.0.0'
LOGGER = logging.getLogger(__name__)

def __virtual__():    
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

    #Trying to find the master-slave resource name and add it to the dict for later usage in salt state to set the resource into maintenance or move it.
    out_resources_xml_1 = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )
    
    out_resources_xml_grep = subprocess.Popen(['grep', '-E', '<clone id=.*multi_state=\"true\"'],
                        stdin=out_resources_xml_1.stdout,
                        stdout=subprocess.PIPE
                        )

    out_resources_xml_awk = subprocess.Popen(['awk', '{print $2}'],
                        stdin=out_resources_xml_grep.stdout,
                        stdout=subprocess.PIPE
                        )

    ms_resource_name = out_resources_xml_awk.communicate()[0].decode("utf-8")
    ms_res_name = ms_resource_name.split('=', 1)
    ms_rs_name = ms_res_name[1].strip()
    ret['msl_resource'] = ms_rs_name.strip('\"')

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
                
                for n in node_status_patterns:
                    
                    if re.search(n, line.decode('utf-8')):
                        
                        ret["Nodes"][c] = "online {}".format(c)
                        ret["node_comment"].append("{} is online but {}.".format(c,n.lstrip(".*")))
                        ret["maintenance_approval"] = False
                    else:
                        ret["Nodes"][c] = "online"

            
            if re.search(offline_pattern, line.decode('utf-8')):
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
            ret['clusterstate'] = line.decode('utf-8').strip()
            if ret['clusterstate'] not in "S_IDLE":
                __salt__["grains.set"]('cluster_state_idle', False)
                ret["dc_comment"] = "cluster state is not S_IDLE, wait until idle."
                ret["maintenance_approval"] = False
                #we end the func if cluster state is not s_idle. Then no need to further query the cluster.
                return ret
            
            if ret['clusterstate'] in "S_IDLE":
                __salt__["grains.set"]('cluster_state_idle', True)
                ret["dc_comment"] = "cluster state is in S_IDLE."
                break

    #finally we query the hana system replication status.
    out1 = subprocess.Popen(['SAPHanaSR-showAttr'], 
                        stdout=subprocess.PIPE,
                        )
    
    if hostname in master_slave_nodes:

        #the secondary node if working correctly has a score value of 2 digits and must be 4:S and SOK
        sok_escaped = '.*[0-9]{2}.*4:S.*SOK'
        search_pattern_sok = "^{}".format(hostname) + sok_escaped
        
        #the primary node if working properly has a score value of 10 digits and 4:P and PRIM
        prim_escaped = '.*[0-9]{10}.*4:P.*PRIM'
        search_pattern_prim = "^{}".format(hostname) + prim_escaped
        #and if SFAIL is found we must set status to maintenance_approval = False
        search_pattern_sfail = "^{}.*SFAIL".format(hostname)

        matches = 0
        fqdnhostname = socket.getfqdn(hostname)

        for line in iter(out1.stdout.readline, b''):        
            if re.search(search_pattern_sok, line.decode('utf-8')):
                ret['sr_status'] = "SOK"
                __salt__['grains.set']('hana_secondary', fqdnhostname, 'force=True')
                
                matches += 1
            if re.search(search_pattern_prim, line.decode('utf-8')):
                __salt__['grains.set']('hana_primary', fqdnhostname, 'force=True')
                ret['sr_status'] = "PRIM"
               
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
        ret['diskless_node'] = True

        __salt__["grains.set"]('diskless_node', True, 'force=True')
        ret["comment"] = "This host is not a HANA host."
    return ret

def sync_status():
    '''
    Show SAP HANA Scale-up pacemaker cluster status.

    CLI Example:

    .. code-block:: bash

        salt '*' bocrm.sync_status
    '''
    crm_ret = _check_crmsh()
    if not crm_ret['status']:
        return crm_ret

    if not bool(__salt__['service.status']("pacemaker")):
        ret = dict()
        ret["comment"] = "pacemaker is not running"
        ret["maintenance_approval"] = False
        return ret
    else:
        ret = _msl_status()
        
        if not ret["maintenance_approval"]:
            __context__["retcode"] = 42
        return ret

def pacemaker():
    return __salt__['service.status']("pacemaker")

def _check_SAPHanaSR_showAttr():
    find_command = '/usr/sbin/SAPHanaSR-showAttr'
    if bool(salt.utils.path.which(find_command)):
        return True
    else:
        return False
    return False


def _check_crmsh():

    if bool(salt.utils.path.which(CRM_COMMAND)):
        version = __salt__['pkg.version'](CRMSH)
        use_crm = __salt__['pkg.version_cmp'](
            version, CRM_NEW_VERSION) >= 0
        LOGGER.info('crmsh version: %s', version)
        LOGGER.info(
            '%s will be used', 'crm')

    else:
        return {'status': False, 'message': 'failed to find binary crm. Check if crmsh is installed.'}

    if not use_crm:
        return {'status': False, 'message': 'crmsh version is too old.'}
    
    #__salt__['crmsh.version'] = use_crm
    return {'status': True, 'message': 'crmsh is installed.'}

def _search_pattern(pattern, inputs):
    
    for line in iter(inputs.stdout.readline, b''):
        if re.search(pattern, line.decode('utf-8')):
            return True    
    return False

def is_quorum():

    out_corosync_quorum_status = subprocess.Popen(['corosync-quorumtool', '-s'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )
    
    expected_votes = 0
    total_votes = 0

    for line in iter(out_corosync_quorum_status.stdout.readline, b''):

        if re.search("Expected votes:", line.decode('utf-8')):
            expected_votes = line.decode('utf-8').split(":")[1].strip()

        if re.search("Total votes:", line.decode('utf-8')):
            total_votes = line.decode('utf-8').split(":")[1].strip()

    if expected_votes == total_votes:

        return True

    return False

def is_cluster_idle():
    __salt__["grains.set"]('cluster_state_idle', False)
    out_crmadmin_dc_lookup = subprocess.Popen(['crmadmin', '-D'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )

    mycmd = ['cut', '-d', ':', '-f', '2']
    out_crmadmin_dc_host = subprocess.Popen(mycmd,
                    stdin=out_crmadmin_dc_lookup.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                    )

    dc_host, err_dc_host = out_crmadmin_dc_host.communicate()
    if not err_dc_host:
        dc_host = dc_host.decode('utf-8')
        dc_host = dc_host.strip()
        if dc_host != "":
            out_cluster_idle_status = subprocess.Popen(['crmadmin', '-q', '-S', dc_host],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )

            for line in iter(out_cluster_idle_status.stdout.readline, b''):
                cluster_state = line.decode('utf-8')
                
                if re.search("S_IDLE", cluster_state):
                    __salt__["grains.set"]('cluster_state_idle', True)
                    return True

    return False

def wait_for_cluster_idle(interval, timeout):
    ret = dict()
    hostname = socket.gethostname()
    fqdnhostname = socket.getfqdn(hostname)
    __salt__["grains.set"]('cluster_state_idle', False)

    if interval <=15:
        interval = 15
    
    if timeout <= 1:
        timeout = 1
    
    timeout = time.time() + 60*timeout

    while True:
        time.sleep(interval)
        
        if is_cluster_idle():
            ret['cluster_state'] = "is idle now."
            __salt__["event.send"]('suma/pacemaker/cluster/state/idle', {"cluster_idle": True, 'node': fqdnhostname})
            __salt__["grains.set"]('cluster_state_idle', True)

            return True

        if time.time() > timeout:
            break
    
    ret['cluster_state'] = "timeout and cluster state is not IDLE yet."
    __context__["retcode"] = 42
    return False

def set_on_msl_maintenance(msl_resource_name):
    hostname = socket.gethostname()
    ret = dict()
    ret['msl_maintenance'] = False

    verify_pattern = "\<clone id=\"{}\" multi_state=\"true\".*managed=\"true\".*>$".format(msl_resource_name)

    out_resources_xml = subprocess.Popen(['crm_mon', '-1', '--exclude=all', '--include=resources', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )
    
    if _search_pattern(verify_pattern, out_resources_xml):
        out_set_maint_mode = subprocess.Popen(['crm', 'resource', 'maintenance', msl_resource_name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
        ret["run_on"] = hostname
        
        out_set_maint_mode.wait()

        if out_set_maint_mode.returncode != 0:
            for line in iter(out_set_maint_mode.stderr.readline, b''): 
                ret['msl_resource_error'] = ''.join(line.decode('utf-8'))

    out_resources_xml_after = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1', '--output-as=xml'],
                        stdout=subprocess.PIPE
                        )
                        
    verify_pattern2 = "\<clone id=\"{}\" multi_state=\"true\".*managed=\"false\".*>$".format(msl_resource_name)

    if _search_pattern(verify_pattern2, out_resources_xml_after):
        ret['msl_maintenance'] = True
        ret['comment'] = "{} is in maintenance mode now.".format(msl_resource_name)
        return ret
                
    return ret

def set_msl_maintenance(msl_resource_name):
    ret = dict()

    crm_ret = _check_crmsh()
    if not crm_ret['status']:
        __context__["retcode"] = 42
        return crm_ret

    if not bool(__salt__['service.status']("pacemaker")):
        ret = dict()
        ret["comment"] = "pacemaker is not running"
        __context__["retcode"] = 42
        return ret
    
    if not is_quorum():
        ret = dict()
        ret["comment"] = "corosync quorum failed. Node does not have quorum partition."
        __context__["retcode"] = 42
        return ret

    if not is_cluster_idle():
        ret = dict()
        ret["comment"] = "cluster state is not S_IDLE."
        __context__["retcode"] = 42
        return ret
    else:
        
        #set msl_SAPHana_BJK_HDB00 to maintenance mode 
        ret = set_on_msl_maintenance(msl_resource_name)
        if not ret["msl_maintenance"]:
            __context__["retcode"] = 42
            return ret

    return ret

def set_off_msl_maintenance(msl_resource_name):
    hostname = socket.gethostname()
    ret = dict()
    ret['msl_maintenance'] = True

    if not bool(__salt__["grains.get"]('cluster_state_idle')):
        ret['commant'] = "Cluster state is not idle."
        __context__["retcode"] = 42
        
        return ret


    verify_pattern = "\<clone id=\"{}\" multi_state=\"true\".*managed=\"false\".*>$".format(msl_resource_name)

    out_resources_xml = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1', '--output-as=xml'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )

    if _search_pattern(verify_pattern, out_resources_xml):
        ret['msl_maintenance'] = True
        ret['comment'] = "{} is still in maintenance mode".format(msl_resource_name)

        out_resources_xml = subprocess.Popen(['crm', 'resource', 'maintenance', msl_resource_name, 'off'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )
        time.sleep(3)
        if out_resources_xml.returncode != 0:
            for line in iter(out_resources_xml.stderr.readline, b''): 
                ret['msl_resource_error'] = ''.join(line.decode('utf-8'))
    
    verify_pattern_after = "\<clone id=\"{}\" multi_state=\"true\".*managed=\"true\".*>$".format(msl_resource_name)

    out_resources_xml = subprocess.Popen(['crm_mon', '--exclude=all', '--include=resources', '-1', '--output-as=xml'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                        )
    if _search_pattern(verify_pattern_after, out_resources_xml):
        ret['msl_maintenance'] = False
        ret['comment'] = "{} is online again.".format(msl_resource_name)

    return ret

def off_msl_maintenance(msl_resource_name):
    ret = dict()

    crm_ret = _check_crmsh()
    if not crm_ret['status']:
        __context__["retcode"] = 42
        return crm_ret

    if not bool(__salt__['service.status']("pacemaker")):
        ret = dict()
        ret["comment"] = "pacemaker is not running"
        __context__["retcode"] = 42
        return ret
    
    if not is_quorum():
        ret = dict()
        ret["comment"] = "corosync quorum failed. Node does not have quorum partition."
        __context__["retcode"] = 42
        return ret
    
    if not is_cluster_idle():
        ret = dict()
        ret["comment"] = "cluster state is not S_IDLE."
        __context__["retcode"] = 42
        return ret
    else:
        #set msl_SAPHana_BJK_HDB00 to maintenance mode 
        ret = set_off_msl_maintenance(msl_resource_name)
        if ret['msl_maintenance']:
            __context__["retcode"] = 42
        return ret

    ret['comment'] = "Something went wrong."
    return ret

def start_pacemaker():
    ret = dict()

    crm_ret = _check_crmsh()

    if not crm_ret['status']:
        __context__["retcode"] = 42
        return crm_ret

    if not bool(__salt__['service.status']("pacemaker")):
        __salt__['service.start']("pacemaker")
    else:
        ret['pacemaker'] = "is already running"
        return ret

    
    if not bool(__salt__['service.status']("pacemaker")):
        ret['pacemaker'] = "Failed to start pacemaker."
        __context__["retcode"] = 42
        
    else:
        ret['pacemaker'] = "running"
    
    return ret

def stop_pacemaker():
    ret = dict()

    crm_ret = _check_crmsh()

    if not crm_ret['status']:
        ret['pacemaker'] = "crmsh is not available.."
        __context__["retcode"] = 42
        return crm_ret

    if not is_quorum():
        ret = dict()
        ret["comment"] = "corosync quorum failed. Node does not have quorum partition. Therefore we don't stop pacemaker."
        __context__["retcode"] = 42
        return ret
    
    if not is_cluster_idle():
        ret = dict()
        ret["comment"] = "cluster state is not S_IDLE therefore not stopping pacemaker."
        __context__["retcode"] = 42
        return ret

    if bool(__salt__['service.status']("pacemaker")):
        __salt__['service.stop']("pacemaker")
    else:
        ret['pacemaker'] = "is already stopped."
        return ret
    
    if bool(__salt__['service.status']("pacemaker")):
        ret['pacemaker'] = "Failed to stop pacemaker."
        __context__["retcode"] = 42
    else:
        ret['pacemaker'] = "stopped"

    return ret


def find_cluster_nodes():
    diskless_node_name = ""
    ret = dict()
    cluster_nodes = []
    cluster_node_info = {}
    cluster_node_info['cluster_nodes'] = []
    hostname = socket.gethostname()
    message_tag = "suma/hana/cluster/nodeinfo/{}".format(hostname)
    #First try to find the pacemaker cluster member nodes.
    out_crm_nodes = subprocess.Popen(['crm', 'node', 'server'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_crm_nodes.stdout.readline, b''):
        #create a list of found nodes.
        cluster_nodes.append(line.decode('utf-8').rstrip())
        cluster_node_info['cluster_nodes'].append(line.decode('utf-8').rstrip())
    #cluster_node_info['cluster_nodes'] = cluster_nodes

    if len(cluster_nodes) <= 2 or len(cluster_nodes) > 3:
        cluster_node_info["diskless_node"] = None

    total_nodes = len(cluster_nodes)
    #print("++++++++++++++ cluster_nodes {}".format(cluster_nodes))

    if _check_SAPHanaSR_showAttr():
        #print("++++++++++++++ cluster_nodes {}".format(cluster_nodes))

        #finally we query the hana system replication status.
        out1 = subprocess.Popen(['SAPHanaSR-showAttr'], 
                            stdout=subprocess.PIPE,
                            )
        
        out2 = subprocess.Popen(['grep', '-A5', '-E', 'Hosts.*clone_state.*node_state'],
                            stdin=out1.stdout, 
                            stdout=subprocess.PIPE,
                            )

        #the secondary node if working correctly has a score value of 2 digits and must be 4:S and SOK
        sok_escaped = '.*online.*4:S.*SOK'
        search_pattern_sok = "^{}".format(hostname) + sok_escaped
        
        #the primary node if working properly has a score value of 10 digits and 4:P and PRIM
        prim_escaped = '.*online.*4:P.*PRIM'
        search_pattern_prim = "^{}".format(hostname) + prim_escaped
        #and if SFAIL is found we must set status to maintenance_approval = False
        search_pattern_sfail = "^{}.*SFAIL".format(hostname)

        for line in iter(out2.stdout.readline, b''):

              
            if re.search(search_pattern_sok, line.decode('utf-8')):
                ret['sr_status'] = "SOK"
                cluster_nodes.remove(hostname)
                cluster_node_info["hana_secondary"] = socket.getfqdn(hostname)
                print("---------- {}".format(line.decode('utf-8')))

            if re.search(search_pattern_prim, line.decode('utf-8')):
                cluster_node_info["hana_primary"] = socket.getfqdn(hostname)
                cluster_nodes.remove(hostname)
                ret['sr_status'] = "PRIM"

            if re.search(search_pattern_sfail, line.decode('utf-8')):
                ret['sr_status'] = "SFAIL"
                cluster_nodes.remove(hostname)
                cluster_node_info["hana_secondary"] = socket.getfqdn(hostname)
                ret["maintenance_approval"] = False
        
        if len(cluster_nodes) == total_nodes:
            cluster_node_info["diskless_node"] = socket.getfqdn(hostname)

        
        __salt__['event.send'](message_tag, {"hana_nodes": cluster_node_info})
    else:
        cluster_node_info["diskless_node"] = hostname
        diskless_node_name = hostname
        __salt__['event.send'](message_tag, {"hana_nodes": cluster_node_info})

    return {"hana_nodes": cluster_node_info}


def patch_diskless_node():

    output = find_cluster_nodes()

    return output
