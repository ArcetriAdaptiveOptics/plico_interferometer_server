# HTTP server startup script, to be run inside 4Sight 2.23 like
# ServerStartup223.py. It replaces the Pyro server: Pyro is not needed.
# Copy plico_interferometer_server/i4sight2 (at least __init__.py and
# HttpServer.py) to C:\Program Files\4Sight2.23\scripts\site-packages\i4sight2
# Clients (plico_interferometer 4SightFocus client, opticalib Wyko) connect
# to http://<this PC>:8011
import sys
sys.path.append('C:\\Program Files\\4Sight2.23\\scripts\\site-packages')

from i4sight2 import HttpServer
wyko_http_server = HttpServer.Server(port=8011)

print('Starting I4D HTTP Server...')
wyko_http_server.start()
print('I4D HTTP Server started on port %d' % wyko_http_server.port)
