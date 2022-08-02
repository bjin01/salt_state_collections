from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path
import subprocess
import socket
import os
import re
import time
import xml.dom.minidom
import xml.etree.ElementTree as ET

__virtualname__ = 'hana_roles'

CRMSH = 'crmsh'
CRM_COMMAND = '/usr/sbin/crm'
CRM_NEW_VERSION = '3.0.0'
LOGGER = logging.getLogger(__name__)

def __virtual__():    
    return __virtualname__

def _get_crm_mon_xml_info():
    # this function should be called by other functions in this module and generate the crm_mon xml output and write output to a file.
    ret = dict()
    try:

        output_crm_node = subprocess.check_output(['crm_mon', '-1', '--output-as=xml']
                        )
    except subprocess.CalledProcessError as e:
        ret["crm_mon_error"] = "Error code: {}, message: {}".format(e.returncode, e.output.decode("utf-8"))
        ret["crm_mon"] = False
        return ret


    output_string = output_crm_node.decode("utf-8")

    with open("/tmp/xmlout.txt","w") as myfile:
        myfile.write(output_string)

    time.sleep(1)
    ret["crm_mon"] = True
    return ret

def find_node_roles_from_crm_mon():
    # this function analyzes crm_mon xml output about node status and returns the node information.
    ret = dict()
    

    ret_get_crm_mon_xml_info = _get_crm_mon_xml_info()

    if ret_get_crm_mon_xml_info["crm_mon"]:
        doc = ET.parse("/tmp/xmlout.txt")
        root_doc = doc.getroot()
        hana_attribute = None

        # value="4:S:master1:master:worker:master"
        for child in root_doc.findall(".//*[@value='4:S:master1:master:worker:master']"):
            #print("-----------------------{} {}".format(child.tag, child.attrib))
            if child.attrib["name"]:
                hana_attribute = child.attrib["name"]

        for child in root_doc.findall(".//*[@value='4:S:master1:master:worker:master']/.."):
            #print("-----------------------{} {}".format(child.tag, child.attrib))
            if child.tag == "node" and child.attrib["name"]:
                ret["hana_secondary"] = child.attrib["name"]
        
        for child in root_doc.findall(".//*[@value='4:P:master1:master:worker:master']/.."):
            #print("-----------------------{} {}".format(child.tag, child.attrib))
            if child.tag == "node" and child.attrib["name"]:
                ret["hana_primary"] = child.attrib["name"]
        
        # name="hana_bjk_roles" value="4:S:master1:master:worker:master"
        if hana_attribute != "":
            for child in root_doc.findall("./node_attributes/node"):
                hana_node = False
                for b in child:
                    #print("-----------------------{} {}".format(b.tag, b.attrib))
                    if hana_attribute in b.attrib:
                        hana_node = True
                if not hana_node:
                    if child.tag == "node" and child.attrib["name"]:
                        ret["diskless_node"] = child.attrib["name"]
        
    if ret["hana_secondary"] and ret["hana_primary"]:
        for a, b in ret.items():
            time.sleep(1)
            __salt__["grains.append"]("hana_info:{}".format(a), b)
    time.sleep(1)
    return ret