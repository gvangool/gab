from fabric.api import *
from fabric.contrib.files import exists, append

from gab.maintenance import apt_update, install
from gab.services import restart
from gab.validators import validate_not_empty as _validate_not_empty


def install_dotfiles(repo='http://github.com/gvangool/dotfiles.git'):
    '''
    Install the dotfiles from the given repository. If none is specified, use
    http://github.com/gvangool/dotfiles/
    '''
    install('git-core')
    run('mkdir -p src')
    run('git clone -nq %s src/dotfiles' % repo)
    run('mv src/dotfiles/.git ~')
    run('git checkout .')
    run('rm -rfd src/dotfiles/')


def install_default_packages():
    '''Install some default packages'''
    install('vim', 'screen', 'lynx', 'smbfs', 'tofrodos')


def install_vcs():
    '''Install most used VCS (svn, git, hg) '''
    install('subversion', 'git-core', 'mercurial')


def install_python(type=''):
    '''Install Python stuff'''
    install('python', 'python-setuptools', 'python-dev', 'build-essential')
    sudo('easyinstall pip')
    sudo('pip install virtualenv virtualenvwrapper')
    if type == 'dev':
        # extra's to build certain python packages
        # needed to build MySQL-python
        install('libmysqlclient15-dev')
        # needed for PIL
        install('libfreetype6-dev', 'libjpeg-dev')


def create_python_env(env_name='generic', requirements_file=None):
    '''
    Create a python virtualenv, based on the given requirements file.
    If no requirements file is given, initialize it we some convenient packages
    '''
    py_env = '~/env/%s' % env_name
    if requirements_file is None:
        run('pip install -E %s ipython suds pygments httplib2 ' % py_env)
        run('pip install -E %s simplejson textile markdown' % py_env)
        run('pip install -E %s django bpython docutils' % py_env)
        pil_url = 'http://effbot.org/downloads/Imaging-1.1.7.tar.gz'
        run('pip install -E %s Imaging==1.1.7 -f %s' % (py_env, pil_url,))
        run('pip install -E %s MySQL-python' % py_env)
    else:
        run('pip install -E %s -r %s' % (py_env, requirements_file))


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
    install('python', 'python-setuptools', 'python-dev', 'build-essential', 'librsync-dev')
    run('pip install -E %s boto' % py_env)
    run('pip install -E %s http://code.launchpad.net/duplicity/0.6-series/0.6.05/+download/duplicity-0.6.05.tar.gz' % py_env)


def install_nginx(stable=True):
    '''Install nginx as a webserver or reverse proxy'''
    if not stable:
        version = '0.8.46'
    install('nginx')  # install it to get stable version and initial config
    if not stable:
        stop('nginx')
        run('mkdir -p src')
        with cd('src'):
            run('wget http://sysoev.ru/nginx/nginx-%s.tar.gz' % version)
            run('tar xf nginx-%s.tar.gz' % version)
            # requirements for nginx
            install('libc6', 'libpcre3', 'libpcre3-dev', 'libpcrecpp0', 'libssl0.9.8', 'libssl-dev', 'zlib1g', 'zlib1g-dev', 'lsb-base')
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
    '''Install Apache2 as a application backend'''
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


def install_apt_cacher(admin='root@localhost'):
    '''Install apt-cacher server'''
    install('apt-cacher')
    sudo('echo AUTOSTART=1 >> /etc/default/apt-cacher')
    sudo('echo \'EXTRAOPT=" admin_email=%s"\' >> /etc/default/apt-cacher' % admin)
    sudo('/etc/init.d/apt-cacher restart')


def install_tmux():
    '''Get and install the latest tmux (1.3)'''
    install('build-essential', 'libevent-dev', 'ncurses-dev')
    run('mkdir -p src')
    with cd('src'):
        run('wget http://downloads.sourceforge.net/project/tmux/tmux/tmux-1.3/tmux-1.3.tar.gz?use_mirror=heanet')
        run('tar xf tmux-1.3.tar.gz')
        with cd('tmux-1.3'):
            run('./configure')
            run('make')
    run('mkdir -p bin')
    run('cp ~/src/tmux-1.3/tmux ~/bin/')


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
    install('cd-discid', 'cdparanoia', 'flac', 'lame', 'mp3gain', 'normalize-audio', 'ruby-gnome2', 'ruby', 'vorbisgain')
    run('mkdir -p src')
    with cd('src'):
        run('wget http://rubyripper.googlecode.com/files/rubyripper-%s.tar.bz2' % version)
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
        append('[account]\nuser = %s\npassword = %s' % (username, password,), '/etc/lastfmsubmitd.conf', use_sudo=True)
        # add user to lastfm group so we can submit
        sudo('adduser %s lastfm' % env.user)
        # setup moc to submit to lastfm on song change (use script from
        # http://lukeplant.me.uk/blog/posts/moc-and-last-fm/ to only submit
        # when we're half way through)
        run('mkdir -p ~/.moc')
        with cd('~/.moc'):
            run('wget http://files.lukeplant.fastmail.fm/public/moc_submit_lastfm')
            run('chmod a+x moc_submit_lastfm')
            append('OnSongChange = "/home/%(user)s/.moc/moc_submit_lastfm --artist %%a --title %%t --length %%d --album %%r"' % env, 'config')


def install_systools():
    'Install extra system tools for convenience (htop, iostat, ...)'
    install('htop', 'iotop', 'sysstat', 'nethogs')


def install_memcached(daemon=False):
    'Install memcached server'
    if not exists('/usr/bin/memcached'):
        install('libevent-dev', 'build-essential')
        run('mkdir -p src')
        with cd('src'):
            run('wget http://memcached.googlecode.com/files/memcached-1.4.5.tar.gz')
            run('tar xf memcached-1.4.5.tar.gz')
            with cd('memcached-1.4.5'):
                args = ['--prefix=', '--exec-prefix=/usr', '--datarootdir=/usr']
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


def install_memcached_client():
    'Install libmemcached as client library for memcached'
    if not exists('/usr/bin/memcached'):
        install_memcached()
    install('libevent-dev', 'build-essential')
    run('mkdir -p src')
    with cd('src'):
        run('wget http://launchpad.net/libmemcached/1.0/0.43/+download/libmemcached-0.43.tar.gz')
        run('tar xf libmemcached-0.43.tar.gz')
        with cd('libmemcached-0.43'):
            run('./configure')
            run('make')
            sudo('make install')
    if not exists('/etc/ld.so.conf.d/local_lib'):
        append('/usr/local/lib/', '/etc/ld.so.conf.d/local_lib', use_sudo=True)
        sudo('ldconfig')


def install_memcached_client_python():
    'Install pylibmc (and thus libmemcached) as client libraries for memcached'
    if not exists('/usr/local/lib/libmemcached.so'):
        install_memcached_client()
    install('python', 'python-setuptools', 'python-dev', 'build-essential')
    run('mkdir -p src')
    with cd('src'):
        run('wget http://pypi.python.org/packages/source/p/pylibmc/pylibmc-1.1.1.tar.gz#md5=e43c54e285f8d937a3f1a916256ecc85')
        run('tar xf pylibmc-1.1.1.tar.gz')
        with cd('pylibmc-1.1.1'):
            if hasattr(env, 'virtual_env') and exists(env.virtual_env):
                run('. %(virtual_env)s/bin/activate; python setup.py install --with-libmemcached=/usr/local/lib' % env)
            else:
                sudo('python setup.py install --with-libmemcached=/usr/local/lib' % env)


def install_solr():
    '''Install SOLR: http://lucene.apache.org/solr/'''
    _install('solr-jetty', 'openjdk-6-jdk')
    sed('/etc/default/jetty', 'NO_START=1', 'NO_START=0', use_sudo=True)
    append('JETTY_HOST=0.0.0.0', '/etc/default/jetty', use_sudo=True)
    # move configuration files to current users dir
    run('mkdir -p etc/solr/conf')
    for f in ('etc/solr/conf/schema.xml', 'etc/solr/conf/solrconfig.xml'):
        run('cp /%(f)s ~/%(f)s' % {'f': f})
        sudo('mv /%(f)s /%(f)s~' % {'f': f})
        sudo('ln -s ~/%(f)s /%(f)s' % {'f': f})


def install_rabbitmq(user, password, vhost):
    l = '/etc/apt/sources.list.d/rabbitmq.list'
    if not exists(l):
        sudo('echo deb http://www.rabbitmq.com/debian/ testing main > %s' % l)
        sudo('wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc -O - | apt-key add -')
        apt_update()
    install('rabbitmq-server')
    # create user and make it the admin
    sudo('rabbitmqctl add_user %s %s' % (user, password,))
    sudo('rabbitmqctl set_admin %s' % user)
    # create vhost
    sudo('rabbitmqctl add_vhost %s' % vhost)
    # add permissions for user to vhost
    sudo('rabbitmqctl set_permissions -p %s %s \'.*\' \'.*\' \'.*\'' % (vhost, user,))
    # delete guest user for safety
    sudo('rabbitmqctl delete_user guest')
    plugin_dir = '/usr/lib/rabbitmq/lib/rabbitmq_server-2.1.0/plugins'
    plugin_files = (
        'http://www.rabbitmq.com/releases/plugins/v2.1.0/mochiweb-2.1.0.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.1.0/webmachine-2.1.0.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.1.0/amqp_client-2.1.0.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.1.0/rabbitmq-mochiweb-2.1.0.ez',
        'http://www.rabbitmq.com/releases/plugins/v2.1.0/rabbitmq-management-2.1.0.ez',
    )
    for file in plugin_files:
        sudo('wget %s -P %s' % (file, plugin_dir,))
    # restart rabbitmq to load plugin
    restart('rabbitmq-server')
