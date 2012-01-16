from fabric.api import *

from gab.install import *
from gab.maintenance import *
from gab.operations import *
from gab.server_density import *
from gab.services import *
from gab.setup import *

def localhost():
    env.hosts = ['localhost']
