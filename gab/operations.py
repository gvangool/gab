import os

from fabric.api import sudo, run, put
from fabric.contrib.files import append, exists


def shell(cmd):
    'Run a shell command'
    if cmd.startswith('sudo'):
        sudo(cmd[5:])
    else:
        run(cmd)


def set_hostname(new_hostname):
    '''
    Set the hostname on the server

    :param str new_hostname: the hostname for the server
    '''
    sudo('echo %s > /etc/hostname' % new_hostname)
    sudo('echo 127.0.1.1\t%s >> /etc/hosts' % new_hostname)
    sudo('hostname -F /etc/hostname')


def set_apt_proxy(host):
    '''
    Set the APT proxy.

    :param str host: the apt-cacher-ng server, should be something like
        http://localhost:3142
    '''
    sudo('echo \'Acquire::http::Proxy "%s";\'  | tee /etc/apt/apt.conf.d/01proxy > /dev/null' %
         (host,)
    )


def create_user(username, password='password', is_admin=True):
    '''
    Create a new user.

    :param str username: the new user to create
    :param str password: the password for the user, default is ``password`` (optional)
    :param bool is_admin: should the user have ``sudo`` rights
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
    '''
    Delete a user and its group

    :param str username: the user to delete
    '''
    sudo('deluser --remove-home %s' % username)
    try:
        sudo('delgroup --only-if-empty %s' % username)
    except:
        pass


def install_crontab(remote, local=None):
    '''
    Install the cron file

    :param str remote: the server file containing the crontab information
    :param str local: the local file containing that servers crontab
        information. This file will be uploaded to ``remote``.
    '''
    if local and os.path.exists(local):
        # check whether we need to create directories
        remote_path = os.path.dirname(remote)
        if remote_path:
            run('mkdir -p %s' % remote_path)
        put(local, remote)
    if not exists(remote.replace('~/', '')):
        return

    run('crontab %s' % (remote,))


def remove_crontab():
    '''Remove the cron file'''
    run('crontab -r')


def install_nginx_config(path, site_name, id='00'):
    '''Install nginx config'''
    from gab.services import restart
    if not exists(path):
        return

    available = '/etc/nginx/sites-available/%s' % site_name
    enabled = '/etc/nginx/sites-enabled/%(id)s_%(site_name)s' % {
            'id': id,
            'site_name': site_name
        }
    if not exists(available):
        sudo('ln -s %s %s' % (path, available))
    if not exists(enabled):
        sudo('ln -s %s %s' % (available, enabled))
    restart('nginx')


def create_rabbitmq_user(user, password, admin):
    '''
    Create a new user on the RabbitMQ server

    :param user str: the username
    :param password str: the password for the given user
    :param admin bool: do we want to make the user an admin?
    '''
    # create user
    sudo('rabbitmqctl add_user %s %s' % (user, password,))
    # make it the admin
    if admin:
        sudo('rabbitmqctl set_admin %s' % user)


def create_rabbitmq_vhost(vhost, user):
    '''
    Create a new vhost in the RabbitMQ server and give the user all permissions
    to that vhost.

    :param vhost str: the vhost
    :param user str: the username
    '''
    # create vhost
    sudo('rabbitmqctl add_vhost %s' % vhost)
    # add permissions for user to vhost
    sudo('rabbitmqctl set_permissions -p %s %s \'.*\' \'.*\' \'.*\'' % (vhost, user,))


def add_ssh_config(hostname, username, identity_file):
    '''
    Add a line to the ssh config file (found in ``~/.ssh/config``).

    E.g. the configuration for github::

        add_ssh_config('github.com', 'git', '~/.ssh/my_gh_key)

    will result in::

        Host github.com
            User git
            Hostname github.com
            IdentityFile ~/.ssh/my_gh_key


    :param hostname str: the external host
    :param username str: the username you need to use when you connect to that
        host, specify ``*`` if it's for all usernames
    :param identity_file str: the location to the private key file
    '''
    v = {'host': hostname, 'user': username, 'key': identity_file, }
    run('echo "Host %(host)s\n'
        '\tUser %(user)s\n'
        '\tHostname %(host)s\n'
        '\tIdentityFile %(key)s" >> ~/.ssh/config' % v)
    run('ssh-keyscan %s >> .ssh/known_hosts' % hostname)
