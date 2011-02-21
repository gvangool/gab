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
    append('127.0.1.1\t%s' % new_hostname, '/etc/hosts', use_sudo=True)
    sudo('hostname -F /etc/hostname')


def set_apt_proxy(host):
    '''
    Set the APT proxy.

    ``host`` should be something like http://localhost:3142
    '''
    sudo('echo Acquire::http::Proxy "%s";  > /etc/apt/apt.conf.d/01proxy' % host)


def create_user(username, password='password', is_admin=True):
    '''
    Create a new user.

    ``username``
        the new user to create
    ``password``
        optionally the password for the user, default is ``password``
    '''
    # create user
    sudo('useradd -U -m -s /bin/bash %s' % username)
    # set password
    sudo('echo "%s:%s" | chpasswd' % (username, password))
    if is_admin:
        # add to admin group (sudoers)
        sudo('adduser %s admin' % username)
        # add to adm group (administrators)
        sudo('adduser %s adm' % username)


def delete_user(username):
    'Delete a user and its group'
    sudo('deluser --remove-home %s' % username)
    try:
        sudo('delgroup --only-if-empty %s' % username)
    except:
        pass


def install_crontab(path):
    '''Install the cron file'''
    if not exists(path):
        return

    run('crontab %s' % (path,))


def remove_crontab():
    '''Remove the cron file'''
    run('crontab -r')


def install_nginx_config(path, site_name, id='00'):
    '''Install nginx config'''
    from gab.services import restart
    if not exists(path):
        return

    sudo('ln -s %s /etc/nginx/sites-available/%s' % (path, site_name,))
    sudo('''ln -s /etc/nginx/sites-available/%(site_name)s \
            /etc/nginx/sites-enabled/%(id)s_%(site_name)s''' % locals())
    restart('nginx')
