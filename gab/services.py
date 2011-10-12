from fabric.api import sudo, run
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.utils import abort

# current format:
# - key -> dict:
#   - type: the service type: upstart or service
#   - restart: support restart? Or a string with the restart command
#   - name: alias for the service (example apache -> apache2)
# - key -> type (shortcut for dict[type])

service_information = {'__default__': {'type': 'upstart',
                                       'restart': False, }, }


#: default stop commands, this should contain every ``type`` of services (e.g.
#: ``upstart``, ``service``)
STOP_CMD = {
    'service': 'service %(service)s stop',
    'upstart': 'stop %(service)s'
}


def add_service_information(name, value):
    '''
    Add extra information for special services

    :param str name: the name of the service
    :param value: the service information. Support formatting: ``{'type': str, 'restart: bool, 'name': str}``
    :type value: str or dict
    '''
    if not isinstance(value, dict):
        value = {'type': value}
    service_information[name] = value


def _name(service):
    '''
    Find the actual service name (expand the aliases)

    :param str service: the service for which you want the real name

    :return: the actual service name
    '''
    info = service_information.get(service, '')
    if 'name' in info:
        return _name(info['name'])
    return service


def _service_info(service):
    '''
    Find the correct service information object

    :param str service: the service for which you want the information dict

    :return: a tuple containing the actual service name and the dict with
        detailed information
    :rtype: tuple
    '''
    # get the real name
    service = _name(service)
    # find the dict or return the default dict
    default = service_information['__default__']
    return (service, service_information.get(service, default))


def _supports_restart(service):
    service, info = _service_info(service)
    if 'restart' in info:
        return info['restart']
    elif 'type' in info:
        return info['type'] != 'upstart'


def _service_type(service):
    service, info = _service_info(service)
    if 'type' in info:
        return info['type']


def _start(service):
    'Start a service'
    service = _name(service)
    st = _service_type(service)
    if st == 'service':
        sudo('service %s start' % service)
    elif st == 'upstart':
        sudo('start %s' % service)


def start(*services):
    '''
    Start a service or a list of services
    '''
    for service in services:
        _start(service)


def _stop(service):
    'Stop a service'
    service, info = _service_info(service)
    if 'stop_cmd' in info:
        stop_cmd = info['stop_cmd']
    elif 'type' in info:
        stop_cmd = STOP_CMD[info['type']]

    with settings(warn_only=True):
        resp = sudo(stop_cmd % {'service': service})
        if not resp.succeeded:
            print resp
            if not confirm(
                    'Something failed while trying to stop %s. Can we continue?' % service,
                    default=True
               ):
                abort('Aborted!')



def stop(*services):
    '''
    Stop a service or a list of services
    '''
    for service in services:
        _stop(service)


def _restart(service):
    'Restart a service'
    service = _name(service)
    st = _service_type(service)
    restart = _supports_restart(service)

    if isinstance(restart, str):
        sudo(restart)
    elif restart and st == 'service':
        sudo('service %s restart' % service)
    else:
        stop(service)
        start(service)


def restart(*services):
    '''
    Restart a service or a list of services
    '''
    for service in services:
        _restart(service)


def _status(service):
    'Status of a service. Note that not all services support this.'
    service = _name(service)
    st = _service_type(service)
    if st == 'service':
        sudo('service %s status' % service)
    elif st == 'upstart':
        sudo('status %s' % service)


def status(*services):
    '''
    Status of a service or a list of services. Note that not all services
    support this.
    '''
    for service in services:
        _status(service)


# initialize the default service
add_service_information('apache', {'name': 'apache2', })
add_service_information('apache2', 'service')
add_service_information('jetty', {'type': 'service', 'restart': False, })
add_service_information('memcached', 'service')
add_service_information(
    'mysql',
    {'type': 'service',
     'stop_cmd': 'service mysql stop; killall mysqld_safe'}
)
add_service_information('nginx', 'service')
add_service_information('rabbitmq', {'name': 'rabbitmq-server', })
add_service_information('rabbitmq-server', 'service')
