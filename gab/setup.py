from gab.maintenance import update, install
from gab.install import (install_default_packages, install_vcs,
                         install_systools, install_python, install_vlc,
                         install_mysql, install_memcached,
                         install_memcached_client_python, install_apache2,
                         install_mysql_client, install_apt_cacher,)

def setup_base():
    update()
    install_default_packages()
    install_vcs()
    install_systools()

def setup_desktop(type=''):
    setup_base()
    install_python(type)
    install_vlc()
    install('unrar', 'nautilus-open-terminal', 'p7zip-full')

def setup_developer_desktop():
    setup_desktop(type='dev')
    install_mysql()
    install_memcached()
    install_memcached_client_python()

def setup_webserver(type='python'):
    setup_base()
    install_python(type='dev')
    install_apache2(type)
    install_mysql_client()

def setup_database():
    setup_base()
    install_mysql()

def setup_apt_cacher(admin='root@localhost'):
    update()
    install_apt_cacher(admin)
