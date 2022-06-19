from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path
import subprocess
import socket

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
            '%s will be used', 'crm' if use_crm else 'ha-cluster')

    else:
        return (
            False,
            'The crmsh execution module failed to load: the crm package'
            ' is not available.')

    if not use_crm and not bool(salt.utils.path.which(CRM_CLUSTERSTATE)):
        return (
            False,
            'Either crmsh and or ClusterTools2 is not installed.'
            ' package is not found.')
    
    #pacemaker_runnung = __salt__['service.status']("pacemaker.service")

    __salt__['crmsh.version'] = use_crm
    return __virtualname__

def _msl_status():
    # SAPHanaSR-showAttr | grep -E "^hana-1.*4:P:master1" | grep PRIM
    # crm_mon -1 | grep -i unmanaged
    # cs_clusterstate | grep -E "^Cluster state" | cut -d ":" -f 2
    # cs_clusterstate | grep -i "Stopped/FAILED" | cut -d ":" -f 2

    out_clusterstate = subprocess.Popen(['cs_clusterstate'],
                        stdout=subprocess.PIPE
                        )
    for line in iter(out_clusterstate.stdout.readline, b''):
        if "Cluster state" in line.decode('utf-8'):
            val = line.decode('utf-8')
            val2 = val.split(": ")
            #print("{0}".format(line.decode('utf-8')), end='')
            print("{0}".format(val2[1].rstrip()))


    """ out_clusterstate = subprocess.Popen(['cs_clusterstate'], 
                        stdout=subprocess.PIPE,
                        )

    grep_cluster_idle_text = "^Cluster state"
    grep_cluster_idle_state = subprocess.Popen(['grep', '-E', grep_cluster_idle_text],
                            universal_newlines=True,
                            shell=True,
                            stdin=out_clusterstate.stdout,
                            stdout=subprocess.PIPE,
                            )
    cut_cluster_idle_output = subprocess.Popen(['cut', '-d', ':', '-f', '2'],
                            universal_newlines=True,
                            shell=True,
                            stdin=grep_cluster_idle_state.stdout,
                            stdout=subprocess.PIPE
                            )
    #cluster_state = repr(cut_cluster_idle_output).strip().lower()
    print("-----------------------------{}------------------".format(cut_cluster_idle_output.communicate()[0].decode().strip()))
    if cut_cluster_idle_output in "transit":
        return "Cluster in transition"

    grep_failed_stopped_text = ".*Stopped/FAILED.*"
    grep_failed_stopped = subprocess.Popen(['grep', '-E',               
                            grep_failed_stopped_text],
                            universal_newlines=True,
                            shell=True,
                            stdin=out_clusterstate.stdout,
                            stdout=subprocess.PIPE,
                            )
    cut_failed_stopped_output = subprocess.Popen(['cut', '-d', ':', '-f', '2'],
                            universal_newlines=True,
                            shell=True,
                            stdin=grep_failed_stopped.stdout
                            stdout=subprocess.PIPE
                            )
    #failed_stopped_value = repr(cut_failed_stopped_output).strip()
    print("-----------------------------{}------------------".format(cut_failed_stopped_output.communicate()[0].decode().strip()))
    if int(cut_failed_stopped_output) != 0:
        return "Failed or stopped resources found. Exit"
 """
    hostname = socket.gethostname()

    out1 = subprocess.Popen(['SAPHanaSR-showAttr'], 
                        stdout=subprocess.PIPE,
                        )

    grep_master_text = "^{}.*4:P:master1.*".format(hostname)
    grep_secondary_text = "^{}.*4:S:master1.*".format(hostname)

    grep_master_out = subprocess.Popen(['grep', '-E', grep_master_text],
                            stdin=out1.stdout,
                            stdout=subprocess.PIPE,
                            )

    primary_status = subprocess.call(['grep', 'PRIM'],
                            stdin=grep_master_out.stdout,
                            stdout=subprocess.PIPE,
                            )
    
    grep_secondary_out = subprocess.Popen(['grep', '-E', grep_secondary_text],
                            stdin=out1.stdout,
                            stdout=subprocess.PIPE,
                            )
    sok_status = subprocess.call(['grep', 'SOK'],
                            stdin=grep_secondary_out.stdout,
                            stdout=subprocess.PIPE,
                            )
    
    sfail_status = subprocess.call(['grep', 'SFAIL'],
                            stdin=grep_secondary_out.stdout,
                            stdout=subprocess.PIPE,
                            )

    if primary_status == 0:
        return "PRIM"
    if sok_status == 0:
        return "SOK"
    if sfail_status == 0:
        return "SFAIL"
    return "UNKNOWN"

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
        output = _msl_status()
        return output

def pacemaker():
    return __salt__['service.status']("pacemaker")
