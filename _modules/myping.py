from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
""" import salt.utils.path
import subprocess
import socket
import os
import re """

__virtualname__ = 'boping'

LOGGER = logging.getLogger(__name__)

def __virtual__():
    '''
    Only load this module if crm package is installed
    '''
    
    return __virtualname__



def ssh_service(name):
    return __salt__['service.available'](name)
