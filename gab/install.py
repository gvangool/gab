from fabric.api import *
from fabric.contrib.files import exists, append, sed

from gab.maintenance import apt_update, install
from gab.services import restart, start, stop
from gab.validators import validate_not_empty as _validate_not_empty


def install_dotfiles(repo='http://github.com/gvangool/dotfiles.git'):
    '''
    Install the dotfiles from the given repository.

    :param str repo: git repository containing the files, default
        http://github.com/gvangool/dotfiles/
    '''
    install('git-core')
    run('mkdir -p src')
    run('git clone -nq %s src/dotfiles' % repo)
    run('mv src/dotfiles/.git ~')
    run('git reset --hard')
    run('git submodule update --init --recursive')
    run('rm -rf src/dotfiles/')


def install_default_packages():
    '''Install some default packages'''
    install('vim', 'screen', 'lynx', 'tofrodos', 'ncurses-term', 'zsh')


def install_vcs():
    '''Install most used VCS (svn, git, hg) '''
    install('subversion', 'git-core', 'mercurial')


def install_python(type=''):
    '''
    Install Python stuff

    :param str type: set type to ``dev`` to install extra libraries (to build
        MySQL-Python and PIL)
    '''
    install('python', 'python-setuptools', 'python-dev', 'build-essential')
    sudo('easy_install pip')
    sudo('pip install -U pip virtualenv virtualenvwrapper')
    if type == 'dev':
        # extra's to build certain python packages
        # needed to build MySQL-python
        install('libmysqlclient-dev')
        # needed for PIL
        install('libfreetype6-dev', 'libjpeg-dev')


def create_python_env(env_name='generic', requirements_file=None):
    '''
    Create a python virtualenv, based on the given requirements file.
    If no requirements file is given, initialize it we some convenient packages
    '''
    py_env = '~/env/%s' % env_name
    if not exists(py_env):
        run('virtualenv --no-site-packages --distribute %s' env_name)
    if requirements_file is None:
        run('%s/bin/pip install ipython suds pygments httplib2 ' % py_env)
        run('%s/bin/pip install simplejson textile markdown' % py_env)
        run('%s/bin/pip install django bpython docutils' % py_env)
        pil_url = 'http://effbot.org/downloads/Imaging-1.1.7.tar.gz'
        run('%s/bin/pip install Imaging==1.1.7 -f %s' % (py_env, pil_url,))
        run('%s/bin/pip install MySQL-python pep8 fabric' % py_env)
    else:
        run('%s/bin/pip install -r %s' % (py_env, requirements_file))


def install_ruby():
    install('ruby1.8', 'libbluecloth-ruby', 'libopenssl-ruby1.8',
            'ruby1.8-dev', 'ri', 'rdoc', 'irb')
    sudo('ln -s /usr/bin/ruby1.8 /usr/bin/ruby')
    # gem install
    run('mkdir -p src')
    with cd('src'):
        run('wget http://production.cf.rubygems.org/rubygems/rubygems-1.3.7.tgz')
        run('tar xvzf rubygems-1.3.7.tgz')
        with cd('rubygems-1.3.7'):
            sudo('ruby setup.rb')
            sudo('ln -s /usr/bin/gem1.8 /usr/bin/gem')


def install_duplicity(env_name='backup'):
    '''Install the duplicity backup tool (http://duplicity.nongnu.org/)'''
    py_env = '~/env/%s' % env_name
    install_python()
    install('librsync-dev')
    run('pip install -E %s boto' % py_env)
    url = 'http://code.launchpad.net/duplicity/0.6-series/0.6.05/+download/duplicity-0.6.05.tar.gz'
    run('pip install -E %s %s' % (py_env, url))


def install_nginx(version=None, remove_default=True):
    '''
    Install nginx as a webserver or reverse proxy

    :param str version: the version of nginx you want to have installed if it's
        a different version than the repository version. E.g. 1.0.4
    '''
    # install from the repository to get stable version and initial config
    install('nginx')
    default_site = '/etc/nginx/sites-enabled/default'
    if remove_default and exists(default_site):
        sudo('rm %s' % default_site)
        restart('nginx')
    # if a version is specified, install that and overwrite the repo version
    if version:
        stop('nginx')
        run('mkdir -p src')
        with cd('src'):
            run('wget http://nginx.org/download/nginx-%s.tar.gz' % version)
            run('tar xf nginx-%s.tar.gz' % version)
            # requirements for nginx
            install('build-essential', 'libc6', 'libpcre3', 'libpcre3-dev',
                    'libpcrecpp0', 'libssl0.9.8', 'libssl-dev', 'zlib1g',
                    'zlib1g-dev', 'lsb-base')
            with cd('nginx-%s' % version):
                run('''./configure --with-http_ssl_module \\
                       --with-sha1=/usr/lib \\
                       --with-http_gzip_static_module \\
                       --with-http_stub_status_module \\
                       --without-http_fastcgi_module \\
                       --sbin-path=/usr/sbin \\
                       --conf-path=/etc/nginx/nginx.conf \\
                       --prefix=/etc/nginx \\
                       --error-log-path=/var/log/nginx/error.log \\
                       ''')
                run('make')
                sudo('make install')
        start('nginx')


def install_apache2(type='python'):
    '''
    Install Apache2 as a application backend

    :param str type: set a type to install some extra apache modules. E.g.
        ``python``, ``php5``, ``ruby``
    '''
    install('apache2', 'libapache2-mod-rpaf')
    if type == 'python':
        install('libapache2-mod-wsgi')
    elif type == 'php5':
        install('libapache2-mod-php5', 'php5', 'php5-mysql', 'php5-gd')
    elif type == 'ruby':
        install_ruby()
        install('apache2-dev')
        sudo('gem install passenger')
        sudo('passenger-install-apache2-module')
        sudo('a2enmod passenger')
    # enable some extra modules
    sudo('a2enmod expires')
    # we want rid of the default apache config
    sudo('a2dissite default')
    restart('apache2')


def install_mysql():
    '''Install MySQL as database'''
    install_mysql_server()
    install_mysql_client()


def install_mysql_server():
    '''Install MySQL server'''
    install('mysql-server-5.1')


def install_mysql_client():
    '''Install MySQL client'''
    install('mysql-client-5.1')


def install_apt_cacher():
    '''Install apt-cacher server'''
    install('apt-cacher-ng')


def install_tmux(version='1.8'):
    '''
    Get and install the latest tmux

    :param str version: the tmux version to install. Default: 1.8
    '''
    install('build-essential', 'libevent-dev', 'ncurses-dev', 'ncurses-term')
    run('mkdir -p src')
    with cd('src'):
        run('wget http://downloads.sourceforge.net/project/tmux/tmux/tmux-%(version)s/tmux-%(version)s.tar.gz?use_mirror=heanet -O tmux-%(version)s.tar.gz' % {'version': version})
        run('tar xf tmux-%s.tar.gz' % version)
        with cd('tmux-%s' % version):
            run('./configure')
            run('make')
    run('mkdir -p bin')
    run('mkdir -p share/man/man1/')
    run('cp ~/src/tmux-%s/tmux ~/bin/' % version)
    run('cp ~/src/tmux-%s/tmux.1 ~/share/man/man1/' % version)


def install_latex():
    '''Install LaTeX'''
    install('texlive', 'texlive-font*', 'texlive-latex*')
    if getattr(env, 'editor', 'vim') == 'vim':
        install('vim-latexsuite')


def install_vlc():
    '''Install VLC media player'''
    install('vlc', 'mozilla-plugin-vlc', 'videolan-doc')


def install_cdripper():
    '''
    Install RubyRipper to convert audio cd to MP3/OGG/Flac/...

    Website: http://wiki.hydrogenaudio.org/index.php?title=Rubyripper
    '''
    version = '0.5.7'
    install('build-essential', 'cd-discid', 'cdparanoia', 'flac', 'lame',
            'mp3gain', 'normalize-audio', 'ruby-gnome2', 'ruby', 'vorbisgain')
    run('mkdir -p src')
    with cd('src'):
        url = 'http://rubyripper.googlecode.com/files/rubyripper-%s.tar.bz2' % version
        run('wget %s' % url)
        run('bzip2 -d rubyripper-%s.tar.bz2' % version)
        run('tar xf rubyripper-%s.tar' % version)
        with cd('rubyripper-%s' % version):
            # default options: gui + command line
            run('./configure --enable-lang-all --enable-gtk2 --enable-cli')
            sudo('make install')


def install_dvdripper():
    '''Install k9copy as DVD ripper'''
    if not exists('/etc/apt/sources.list.d/medibuntu.list'):
        sudo('wget http://www.medibuntu.org/sources.list.d/$(lsb_release -cs).list --output-document=/etc/apt/sources.list.d/medibuntu.list')
        apt_update()
        install('medibuntu-keyring', allow_unauthenticated=True)
        apt_update()
    install('libdvdcss2')
    install('k9copy')


def install_wine():
    '''Install wine'''
    install('wine')


def install_moc(add_lastfm=True):
    '''
    Install the MOC music player (http://moc.daper.net/). It will also install
    lastfmsubmitd (http://www.red-bean.com/decklin/lastfmsubmitd/) and set it
    up to submit your plays
    '''
    apps = ['moc']
    if add_lastfm:
        apps += ['lastfmsubmitd']
    install(*apps)

    if add_lastfm:
        username = prompt('Last.fm username?', validate=lambda v: _validate_not_empty(v, key='username'))
        password = prompt('Last.fm password?', validate=lambda v: _validate_not_empty(v, key='password'))
        # create lastfm config
        append('/etc/lastfmsubmitd.conf',
               '[account]\nuser = %s\npassword = %s' % (username, password, ),
               use_sudo=True)
        # add user to lastfm group so we can submit
        sudo('adduser %s lastfm' % env.user)
        # setup moc to submit to lastfm on song change (use script from
        # http://lukeplant.me.uk/blog/posts/moc-and-last-fm/ to only submit
        # when we're half way through)
        run('mkdir -p ~/.moc')
        with cd('~/.moc'):
            run('wget http://files.lukeplant.fastmail.fm/public/moc_submit_lastfm')
            run('chmod a+x moc_submit_lastfm')
            append('config',
                   'OnSongChange = "/home/%(user)s/.moc/moc_submit_lastfm --artist %%a --title %%t --length %%d --album %%r"' % env)


def install_systools():
    'Install extra system tools for convenience (htop, iostat, ...)'
    install('htop', 'iotop', 'sysstat', 'nethogs')


def install_memcached(version='1.4.9', daemon=False):
    'Install memcached server'
    if not exists('/usr/bin/memcached'):
        install('libevent-dev', 'build-essential')
        run('mkdir -p src')
        with cd('src'):
            run('wget http://memcached.googlecode.com/files/memcached-%s.tar.gz' % version)
            run('tar xf memcached-%s.tar.gz' % version)
            with cd('memcached-%s' % version):
                args = ['--prefix=', '--exec-prefix=/usr',
                        '--datarootdir=/usr']
                if getattr(env, 'is_64bit', False):
                    args.append('--enable-64bit')
                run('./configure %s' % ' '.join(args))
                run('make')
                sudo('make install')
                sudo('mkdir -p /usr/share/memcached')
                sudo('cp -R scripts /usr/share/memcached')

    if daemon:
        sudo('cp /usr/share/memcached/scripts/memcached-init /etc/init.d/memcached')
        sudo('update-rc.d memcached defaults')
        start('memcached')


def install_memcached_client(version='0.53'):
    'Install libmemcached as client library for memcached'
    if not exists('/usr/bin/memcached'):
        install_memcached()
    install('libevent-dev', 'build-essential')
    run('mkdir -p src')
    with cd('src'):
        v = {'version': version}
        run('wget http://launchpad.net/libmemcached/1.0/%(version)s/+download/libmemcached-%(version)s.tar.gz' % v)
        run('tar xf libmemcached-%(version)s.tar.gz' % v)
        with cd('libmemcached-%(version)s' % v):
            run('./configure')
            run('make')
            sudo('make install')
    if not exists('/etc/ld.so.conf.d/local_lib'):
        append('/etc/ld.so.conf.d/local_lib', '/usr/local/lib/', use_sudo=True)
        sudo('ldconfig')


def install_memcached_client_python():
    'Install pylibmc (and thus libmemcached) as client libraries for memcached'
    if not exists('/usr/local/lib/libmemcached.so'):
        install_memcached_client('0.50')
    install('python', 'python-setuptools', 'python-dev', 'build-essential', 'zlib1g-dev')
    if hasattr(env, 'virtual_env') and exists(env.virtual_env):
        run('%(virtual_env)s/bin/pip install pylibmc' % env)
    else:
        sudo('pip install pylibmc')


def install_redis(version):
    'Install redis server'
    run('mkdir -p src')
    with cd('src'):
        v = {'version': version}
        run('wget http://redis.googlecode.com/files/redis-%(version)s.tar.gz' % v)
        run('tar xzf redis-%(version)s.tar.gz' % v)
        with cd('redis-%(version)s' % v):
            run('make')
            sudo('make install')


def install_solr():
    '''Install SOLR: http://lucene.apache.org/solr/'''
    install('solr-jetty', 'openjdk-6-jdk')
    sed('/etc/default/jetty', 'NO_START=1', 'NO_START=0', use_sudo=True)
    append('/etc/default/jetty', 'JETTY_HOST=0.0.0.0', use_sudo=True)
    # move configuration files to current users dir
    run('mkdir -p etc/solr/conf')
    for f in ('etc/solr/conf/schema.xml', 'etc/solr/conf/solrconfig.xml'):
        run('cp /%(f)s ~/%(f)s' % {'f': f})
        sudo('mv /%(f)s /%(f)s~' % {'f': f})
        sudo('ln -s ~/%(f)s /%(f)s' % {'f': f})


def install_rabbitmq(user, password, vhost):
    '''Install the RabbitMQ server and add the web management plugin'''
    from gab.operations import create_rabbitmq_user, create_rabbitmq_vhost
    l = '/etc/apt/sources.list.d/rabbitmq.list'
    if not exists(l):
        sudo('echo deb http://www.rabbitmq.com/debian/ testing main > %s' % l)
        sudo('wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc -O - | apt-key add -')
        apt_update()
    install('rabbitmq-server', 'erlang-inets')
    # create the user & make it the admin
    create_rabbitmq_user(user, password, admin=True)
    # create the vhost
    create_rabbitmq_vhost(vhost, user)
    # delete guest user for safety
    sudo('rabbitmqctl delete_user guest')
    install_rabbitmq_plugins()


def install_rabbitmq_plugins():
    plugin_dir = '/usr/lib/rabbitmq/lib/rabbitmq_server-2.6.1/plugins'
    plugin_files = (
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/mochiweb-1.3-rmq2.6.1-git9a53dbd.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/webmachine-1.7.0-rmq2.6.1-hg0c4b60a.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/amqp_client-2.6.1.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/rabbitmq_mochiweb-2.6.1.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/rabbitmq_management-2.6.1.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.6.1/rabbitmq_management_agent-2.6.1.ez',
    )
    for file in plugin_files:
        sudo('wget %s -P %s' % (file, plugin_dir,))
    # restart rabbitmq to load plugin
    restart('rabbitmq-server')


def install_uwsgi():
    '''
    Install libraries required for uWSGI_ and install uWSGI_ in an test
    virtualenv

    .. _uWSGI: http://projects.unbit.it/uwsgi/
    '''
    install('libxml2-dev')
    run('pip install -E ~/env/uwsgi_test uwsgi')


def install_kvm():
    '''Install KVM & virsh for virtualization'''
    install('libvirt-bin', 'qemu-kvm')
