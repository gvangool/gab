from fabric.api import *
from fabric.contrib.files import exists

from gab.validators import yes_or_no as _yes_or_no


def _apt_get(cmd):
    '''
    Wrapper for ``apt-get``. This will set the :envvar:`DEBIAN_FRONTEND` to
    ``noninteractive``.

    :param str cmd: the rest of the ``apt-get`` command
    '''
    return sudo('export DEBIAN_FRONTEND=noninteractive; apt-get %s' % cmd)


def update(dselect=False):
    '''
    Update everything. It will update & upgrade all installed packages.

    :param bool dselect: whether or not to trigger the
        ``apt-get dselect-upgrade`` behaviour.
    '''
    apt_update()
    apt_upgrade(dselect)


def apt_update():
    'Update apt repositories'
    _apt_get('update -q')


def apt_upgrade(dselect=False):
    '''
    Upgrade installed packages

    :param bool dselect: whether or not to trigger the
        ``apt-get dselect-upgrade`` behaviour.
    '''
    _apt_get('upgrade -yq')
    if dselect:
        # download only
        _apt_get('dselect-upgrade -yqd')
        # ask user whether he wants to run it
        if not getattr(env, 'silent', True) and \
           prompt('Do you want to run "apt-get dist-upgrade"? ',
                  default='y',
                  validate=_yes_or_no):
            _apt_get('dselect-upgrade -yqq')


def install(*package_list, **options):
    '''
    Install packages

    :param list package_list: a list of packages to install
    :param dict options: pass extra options to ``apt-get``. Supported options:
        ``allow_unauthenticated`` (``True`` or ``False``)
    '''
    if len(package_list) == 0:
        return

    args = '-yq'
    if options.get('allow_unauthenticated', False):
        args += ' --allow-unauthenticated'
    package_list = ' '.join(package_list)
    _apt_get('install %s %s' % (args, package_list,))
