# salt execution module - crmhana - Query and check SAP HANA SR Scale-up pacemaker cluster status

The purpose of this execution module is to check SAP HANA system replication scale-up cluster status and set a maintenance_approval status that indicates if the cluster nodes can be further patched or not. The module should help linux admins to automate certain patching steps within their regular OS maintenance windows. 

The maintenance_approval will be set to True if:
* crmsh package is installed
* all cluster member nodes are only and not in failed or unmanaged state
* no pacemaker resource/clone-set is in maintenance or failed state
* designated controller is found
* clusterstate is in S_IDLE and not in transition or others
* master and slave nodes of the for example: msl_SAPHana_BJK_HDB00 have been identified
* HANA system replication status on primary node is PRIM and secondary node is SOK.

__If all above conditions have been met then the ```ret["maintenance_approval"] = True``` will be given.__

__*Note:*__ the salt module name has been changed in below to "bocrm". Feel free to change this module name in the crmhana.py line ```__virtualname__ = 'bocrm'``` 

## Usage:
Download the crmhana.py to the local salt-master node's file_roots e.g. /srv/salt
```
wget https://github.com/bjin01/salt_state_collections/blob/main/_modules/crmhana.py -O /srv/salt/_modules/
```
Sync the new module file to the minions. Below command will sync out to all nodes with names hana.
```
salt "hana*" saltutil.sync_all
```

Test the module on SAP HANA SR Scale-Up Cluster nodes:
```
salt "hana-*" bocrm.sync_status
```

Sample output:
```
suma1:/srv/salt/myhana # salt "hana*" bocrm.sync_status 
hana-2.bo2go.home:
    ----------
    Designated Controller:
        hana-1
    Nodes:
        ----------
        hana-1:
            online
        hana-2:
            online
        hana-3:
            online
    clusterstate:
        S_IDLE
    maintenance_approval:
        True
    msl_resource:
        msl_SAPHana_BJK_HDB00
    node_comment:
    resource_comment:
    resources:
    sr_status:
        SOK
hana-3.bo2go.home:
    ----------
    Designated Controller:
        hana-1
    Nodes:
        ----------
        hana-1:
            online
        hana-2:
            online
        hana-3:
            online
    clusterstate:
        S_IDLE
    comment:
        This host is not a HANA host.
    maintenance_approval:
        True
    msl_resource:
        msl_SAPHana_BJK_HDB00
    node_comment:
    resource_comment:
    resources:
    sr_status:
        None
hana-1.bo2go.home:
    ----------
    Designated Controller:
        hana-1
    Nodes:
        ----------
        hana-1:
            online
        hana-2:
            online
        hana-3:
            online
    clusterstate:
        S_IDLE
    maintenance_approval:
        True
    msl_resource:
        msl_SAPHana_BJK_HDB00
    node_comment:
    resource_comment:
    resources:
    sr_status:
        PRIM
```