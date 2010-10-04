from fabric.api import *
from fabric.contrib.files import exists

from gab.validators import yes_or_no as _yes_or_no


def update():
    '''Update all'''
    apt_update()
    _upgrade()
    vcs_update = {'git': 'git pull', 'hg': 'hg update', 'svn': 'svn up'}
    if exists('.git'):
        run(vcs_update['git'])
    if exists('.svn'):
        run(vcs_update['svn'])
    if exists('.repos'):
        # read the file and find all the existing repositories
        get('~/.repos', '/tmp/repos')
        f = open('/tmp/repos')
        for line in f.readlines():
            line = line.strip()
            parts = line.split(' ')
            with cd(parts[1]):
                run(vcs_update[parts[0]])


def apt_update():
    sudo('export DEBIAN_FRONTEND=noninteractive; apt-get update -q')


def _upgrade():
    sudo('export DEBIAN_FRONTEND=noninteractive; apt-get upgrade -yq')
    if not getattr(env, 'silent', True):
        # download only
        sudo('export DEBIAN_FRONTEND=noninteractive; apt-get dist-upgrade -d')
        # ask user whether he wants to run it
        if prompt('Do you want to run "apt-get dist-upgrade"? ',
                  default='y',
                  validate=_yes_or_no):
            sudo('export DEBIAN_FRONTEND=noninteractive; apt-get dist-upgrade -yqq')


def install(*package_list, **options):
    if len(package_list) == 0:
        return

    args = '-yq'
    if options.get('allow_unauthenticated', False):
        args += ' --allow-unauthenticated'
    package_list = ' '.join(package_list)
    sudo('export DEBIAN_FRONTEND=noninteractive; apt-get install %s %s' % (args, package_list,))
