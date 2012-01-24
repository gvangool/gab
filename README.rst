===
GAB
===
A collection of fabfile_ commands I created for easier maintenance of my
servers. Commands are created and tested for Ubuntu_ systems, but should
generally work on Debian_ too.

.. _fabfile: http://fabfile.org
.. _Ubuntu: http://ubuntu.com
.. _Debian: http://debian.org

Changelog
=========
v1.0.1
------
- Install ``ncurses-term`` when compiling tmux (it adds supports for ``$TERM``
  values like ``gnome-256color``)
- Use correct version in ``setup.py``

v1.0.0
------
Initial release
