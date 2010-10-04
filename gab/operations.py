from fabric.api import sudo, run
from fabric.contrib.files import append


def shell(cmd):
    'Run a shell command'
    if cmd.startswith('sudo'):
        sudo(cmd[5:])
    else:
        run(cmd)


def set_hostname(new_hostname):
    'Set the hostname on the server'
    sudo('echo %s > /etc/hostname' % new_hostname)
    append('127.0.0.1\t%s' % new_hostname, '/etc/hosts', use_sudo=True)


def set_apt_proxy(host):
    '''
    Set the APT proxy.

    ``host`` should be something like http://localhost:3142
    '''
    sudo('echo Acquire::http::Proxy "%s";  > /etc/apt/apt.conf.d/01proxy' % host)
