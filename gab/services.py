from fabric.api import sudo, run

# current format:
# - key -> dict:
#   - type: the service type: upstart or service
#   - restart: support restart? Or a string with the restart command
#   - name: alias for the service (example apache -> apache2)
# - key -> type (shortcut for dict[type])

service_information = {'__default__': {'type': 'upstart',
                                       'restart': False,},}


def add_service_information(name, value):
    if not isinstance(value, dict):
        value = {'type': value}
    service_information[name] = value


def _name(service):
    info = service_information.get(service, '')
    if 'name' in info:
        return info['name']
    return service


def _supports_restart(service):
    default = service_information['__default__']
    info = service_information.get(service, default)
    if 'restart' in info:
        return info['restart']
    elif 'type' in info:
        return info['type'] != 'upstart'
    elif 'name' in info:
        return _supports_restart(info['name'])


def _service_type(service):
    default = service_information['__default__']
    info = service_information.get(service, default)
    if 'type' in info:
        return info['type']
    elif 'name' in info:
        return _service_type(info['name'])


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
    service = _name(service)
    st = _service_type(service)
    if st == 'service':
        sudo('service %s stop' % service)
        if service == 'mysql':
            # Due to a minor MySQL bug this may be necessary
            try:
                sudo('killall mysqld_safe')
            except:
                pass
    elif st == 'upstart':
        sudo('stop %s' % service)


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
add_service_information('apache', {'name': 'apache2',})
add_service_information('apache2', 'service')
add_service_information('jetty', {'type': 'service', 'restart': False,})
add_service_information('memcached', 'service')
add_service_information('mysql', 'service')
add_service_information('nginx', 'service')
add_service_information('rabbitmq', {'name': 'rabbitmq-server',})
add_service_information('rabbitmq-server', 'service')
