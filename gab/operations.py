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
