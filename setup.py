#!/usr/bin/env python
from setuptools import setup

import gab

setup(name='gab',
      version=gab.__version__,
      description='Gert\'s fabfiles',
      author='Gert Van Gool',
      author_email='gertvangool@gmail.com',
      url='https://github.com/gvangool/gab/',
      packages=['gab'],
      license='BSD',
      zip_safe = False,
      install_requires=['setuptools', 'fabric',],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
      ],
)


