#!/usr/bin/env python
#
# $Id: setup.py,v 2.26 2005/05/26 21:25:14 irmen Exp $
# Pyro setup script
#

from distutils.core import setup
import sys
import os

from ConfigParser import ConfigParser


def gather_scripts():
    names = ['es', 'genguid', 'ns', 'nsc', 'rns', 'xnsc', 'wxnsc']
    if sys.platform == 'win32':
        names.extend(['nssvc', 'essvc'])  # scripts that are only for Windows
        names = map(lambda x: x + '.bat', names)
    else:
        names.extend(['esd', 'nsd'])  # scripts that are not for Windows
    names = map(lambda x: os.path.join('bin', x), names)
    return names


if __name__ == '__main__':
    scripts = gather_scripts()

    ver = open(os.path.join('Pyro', 'constants.py'), 'r').read()
    ver = ver[ver.find('VERSION'):].split('\'')[1]
    print('Pyro Version: %s' % ver)

    setup(name="Pyro",
          version=ver,
          license="MIT",
          description="Powerful but easy-to-use distributed object middleware for Python",
          author="Irmen de Jong",
          author_email="irmen@users.sourceforge.net",
          url="http://pyro.sourceforge.net/",
          long_description="""Pyro is an acronym for PYthon Remote Objects. It is an advanced and powerful Distributed Object Technology system written entirely in Python, that is designed to be very easy to use. It resembles Java's Remote Method Invocation (RMI). It has less similarity to CORBA - which is a system- and language independent Distributed Object Technology and has much more to offer than Pyro or RMI. But Pyro is small, simple and free!""",
          packages=['Pyro', 'Pyro.EventService', 'Pyro.ext'],
          scripts=scripts,
          platforms='any'
          )
