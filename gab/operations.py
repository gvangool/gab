from fabric.api import sudo, run


def shell(cmd):
    'Run a shell command'
    if cmd.startswith('sudo'):
        sudo(cmd[5:])
    else:
        run(cmd)
