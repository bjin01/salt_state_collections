

from __future__ import absolute_import, print_function, unicode_literals

# Import python libs
import atexit
import logging
# Import third party libs
from salt.ext import six
from datetime import datetime,  timedelta

__virtualname__ = "bopillar"
log = logging.getLogger(__name__)

_sessions = {}


def __virtual__():
    '''
    Check for spacewalk configuration in master config file
    or directory and load runner only if it is specified
    '''
    if not _get_spacewalk_configuration():
        return False, 'No spacewalk configuration found'
    return __virtualname__


def _get_spacewalk_configuration(spacewalk_url=''):
    '''
    Return the configuration read from the master configuration
    file or directory
    '''
    spacewalk_config = __opts__['spacewalk'] if 'spacewalk' in __opts__ else None

    if spacewalk_config:
        try:
            for spacewalk_server, service_config in six.iteritems(spacewalk_config):
                username = service_config.get('username', None)
                password = service_config.get('password', None)
                protocol = service_config.get('protocol', 'https')

                if not username or not password:
                    log.error(
                        'Username or Password has not been specified in the master '
                        'configuration for %s', spacewalk_server
                    )
                    return False

                ret = {
                    'api_url': '{0}://{1}/rpc/api'.format(protocol, spacewalk_server),
                    'username': username,
                    'password': password
                }

                if (not spacewalk_url) or (spacewalk_url == spacewalk_server):
                    return ret
        except Exception as exc:  # pylint: disable=broad-except
            log.error('Exception encountered: %s', exc)
            return False

        if spacewalk_url:
            log.error(
                'Configuration for %s has not been specified in the master '
                'configuration', spacewalk_url
            )
            return False

    return False


def _get_client_and_key(url, user, password, verbose=0):
    '''
    Return the client object and session key for the client
    '''
    session = {}
    session['client'] = six.moves.xmlrpc_client.Server(url, verbose=verbose, use_datetime=True)
    session['key'] = session['client'].auth.login(user, password)

    return session


def _disconnect_session(session):
    '''
    Disconnect API connection
    '''
    session['client'].auth.logout(session['key'])


def _get_session(server):
    '''
    Get session and key
    '''
    if server in _sessions:
        return _sessions[server]

    config = _get_spacewalk_configuration(server)
    if not config:
        raise Exception('No config for \'{0}\' found on master'.format(server))

    session = _get_client_and_key(config['api_url'], config['username'], config['password'])
    atexit.register(_disconnect_session, session)

    client = session['client']
    key = session['key']
    _sessions[server] = (client, key)

    return client, key


def ext_pillar(minion_id, pillar, *args, **kwargs):

    my_pillar = {"external_pillar": {}}

    my_pillar["external_pillar"] = get_external_pillar_dictionary()
    my_pillar["external_pillar"]['sumagroups'] = get_groups(minion_id)
    log.info("-----------{}-----{}--------------".format(minion_id, my_pillar))
    return my_pillar


def get_external_pillar_dictionary():
    data = {}
    data["aaa"] = "123"
    data["bbb"] = "456"
    return data


def get_groups(minion_id, **kwargs):
    server = "suma1.bo2go.home"
    groups = []

    try:
        client, key = _get_session(server)
    except Exception as exc:  # pylint: disable=broad-except
        err_msg = 'Exception raised when connecting to spacewalk server ({0}): {1}'.format(server, exc)
        log.error(err_msg)
        
        return {'Error': err_msg}
    try:
        systemid = client.system.getId(key, minion_id)
    except Exception as exc:  # pylint: disable=broad-except
        err_msg = 'Exception raised when trying to get system ID ({0}): {1}'.format(server, exc)
        log.error(err_msg)
        
        return {'Error': err_msg}

    try:
        grouplist = client.system.listGroups(key, systemid[0]['id'])
    except Exception as exc:  # pylint: disable=broad-except
        err_msg = 'Exception raised when trying to get system group list ({0}): {1}'.format(server, exc)
        log.error(err_msg)
        
        return {'Error': err_msg}
    
    if len(grouplist) != 0: 
        for i in grouplist:
            if i['subscribed'] == 1:
                groups.append(i['system_group_name']) 
    

    return groups
    