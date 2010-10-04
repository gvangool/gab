from fabric.api import sudo, run


def __is_service(service):
    services = ('nginx', 'apache2', 'mysql', 'memcached', 'jetty',
                'rabbitmq-server')
    return service in services


def start(service):
    'Start a service'
    if service == 'apache':
        service = 'apache2'
    if __is_service(service):
        sudo('service %s start' % service)
    else:
        sudo('start %s' % service)


def stop(service):
    'Stop a service'
    if service == 'apache':
        service = 'apache2'
    if __is_service(service):
        sudo('service %s stop' % service)
        if service == 'mysql':
            # Due to a minor MySQL bug this may be necessary
            try:
                sudo('killall mysqld_safe')
            except:
                pass
    else:
        sudo('stop %s' % service)


def restart(service):
    'Restart a service'
    if service == 'apache':
        service = 'apache2'

    if service == 'jetty':
        stop(service)
        start(service)
    #elif service == 'apache2':
    #    sudo('/usr/sbin/apache2ctl graceful')
    elif __is_service(service):
        sudo('service %s restart' % service)
    else:
        sudo('stop %s' % service)
        sudo('start %s' % service)


def status(service):
    'Status of a service. Note that not all services support this.'
    if service == 'apache':
        service = 'apache2'
    if __is_service(service):
        sudo('service %s status' % service)
    else:
        sudo('status %s' % service)
