from shaptools import hana
import logging

log = logging.getLogger(__name__)

def status():
    """
    A function to query SAP HANA information!

    Create a pillar as below::
    myhana:
      hana-1.bo2go.home:
        sid: bjk
        instance: 00
      hana-2.bo2go.home:
        sid: bjk
        instance: 00

    CLI Example::

        salt '*' myhana.status
    """
    remotehost =  __grains__["fqdn"]
    
    sid =  __pillar__['saphana'][remotehost]['sid']
    instno =  __pillar__['saphana'][remotehost]['instance']
    log.info("%s %s %s"%(remotehost, sid, instno))
    h = hana.HanaInstance(sid, instno, '', remote_host=remotehost)
    try:
        return "Installed: {} \nRunning: {} \nSR enabled: {} \nSR Status: {}.".format(h.is_installed(), h.is_running(), h.get_sr_state(), h.get_sr_status()['status'])
    except:
        return "Error, it seems HANA is not installed or mounted at all."