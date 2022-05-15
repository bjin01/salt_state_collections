from shaptools import hana
import logging

log = logging.getLogger(__name__)

log.info("Here is Some Information")
log.warning("You Should Not Do That")
log.error("It Is Busted")

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
    h = hana.HanaInstance('bjk', '00', '', remote_host=remotehost)
    return "Installed: {} \nRunning: {} \nSR enabled: {} \nSR Status: {}.".format(h.is_installed(), h.is_running(), h.get_sr_state(), h.get_sr_status()['status'])