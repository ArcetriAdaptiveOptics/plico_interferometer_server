#! /usr/bin/env python

import sys
from Pyro.ext import remote_nons
import object



# if you don't like the objects to be registered in the Default namespace
# uncomment the following two lines, and use the 'nsc' tool to create
# the appropriate name group:
# import Pyro
# Pyro.config.PYRO_NS_DEFAULTGROUP=":mygroup"

print 'Providing local object as "quickstart"...'
remote_nons.provide_server_object(object.myObject(), 'quickstart',
                                'localhost', object.PYRO_PORT)

print 'Waiting for requests.'
sys.exit(remote_nons.handle_requests())

