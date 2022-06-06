# Pyro Server startup script
# Put this script - and ONLY this - in the Wyko4100 PC in
# C:\Program Files\\4Sight2.23
# Add the i4sight223 Pyro Server package location to path
import sys
sys.path.append('C:\Program Files\\4Sight2.4\scripts\site-packages')
# In site_packages\i4sight223 there must be Commons.py, Controller.py, Server.py
# In site_packages\Pyro there must be the Pyro *.py package (core.py, ...)
# In site_packages there must be dircache.py and md5.py that are needed by Pyro
# and are not provided in the 4sight2.23 python installation


# Create the Server
from i4sight223 import Server
wyko_server = Server.Server()

# Start the Server
print('Starting I4D Pyro Server Daemon...')
wyko_server.start()
print('I4D Pyro Server Daemon started !')


# Test the Controller
# from i4sight223 import Controller
# print('Testing I4D Controller...')
# controller = Controller.Controller()
# wf=controller.wavefront()
# print('I4D Controller tested!')
