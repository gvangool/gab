from fabric.api import sudo
from fabric.contrib.files import exists, append, sed

from gab.maintenance import apt_update, install
from gab.services import start, restart, add_service_information


__all__ = ['install_serverdensity', 'sd_add_apache', 'sd_add_nginx_status',
           'sd_add_rabbitmq_config']


def install_serverdensity(url, key):
    '''
    Install the `Server Density <http://serverdensity.com/>`_ software.

    :param str url: is the chosen url at Server Density:
        https://example.serverdensity.com
    :param str key: the key for the given server. You can find this in the
        server list at Server Density.
    '''
    l = '/etc/apt/sources.list.d/serverdensity.list'
    if not exists(l):
        sudo('echo deb http://www.serverdensity.com/downloads/linux/debian lenny main > %s' % l)
        sudo('wget http://www.serverdensity.com/downloads/boxedice-public.key -O - | apt-key add -')
        apt_update()
    install('sd-agent')
    config = '''
[Main]
sd_url: %(url)s
agent_key: %(key)s
''' % {'url': url,
       'key': key}
    append('/etc/sd-agent/config.cfg', config, use_sudo=True)
    start('sd-agent')


def _update_config(line):
    '''
    Update the ServerDensity agent and restart it.

    :param str line: the extra data for sd-agent
    '''
    append('/etc/sd-agent/config.cfg', line, use_sudo=True)
    restart('sd-agent')


def sd_add_apache(status_url='http://127.0.0.1/server-status'):
    '''
    Add apache monitoring to the ServerDensity agent.
    More information can be found at
    http://www.serverdensity.com/docs/agent/apachestatus/

    :param str status_url: Pass the location of the server-status. Default is
        http://127.0.0.1/server-status
    '''
    _update_config('apache_status_url: %s?auto' % status_url)


def sd_add_nginx_status(status_url='http://127.0.0.1/nginx_status'):
    '''
    Add nginx monitoring to the ServerDensity agent.
    More information can be found at
    http://www.serverdensity.com/docs/agent/nginxstatus/

    :param str status_url: Pass the location of the nginx status page. Default
        is http://127.0.0.1/nginx_status
    '''
    _update_config('nginx_status_url: %s' % status_url)


def sd_add_rabbitmq_config(http_api='http://127.0.0.1:55672/api/overview',
                           user='guest', passwd='guest'):
    '''
    Add RabbitMQ monitoring to the ServerDensity agent.

    :param str http_api: location of the HTTP API
    :param str user: username for RabbitMQ. Default ``guest``
    :param str passwd: password for RabbitMQ. Default ``guest``
    '''
    _update_config('''rabbitmq_status_url: %(http_api)s
rabbitmq_user: %(user)s
rabbitmq_pass: %(passwd)s''' % locals())


add_service_information('sd-agent', 'service')
