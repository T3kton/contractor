from django.conf import settings

from cinp.server_werkzeug import WerkzeugServer, NoCINP

from contractor.Auth.models import getUser
from contractor.lib.config_handler import handler as config_handler

# get plugins

import os
from contractor import plugins

plugin_list = []
plugin_dir = os.path.dirname( plugins.__file__ )
for item in os.scandir( plugin_dir ):
  if not item.is_dir() or not os.path.exists( os.path.join( plugin_dir, item.name, 'models.py' ) ):
    continue
  plugin_list.append( 'contractor.plugins.{0}'.format( item.name ) )


def get_app( debug ):
  app = WerkzeugServer( root_path='/api/v1/', root_version='0.9', debug=debug, get_user=getUser, cors_allow_list=[ '*' ], debug_dump_location=settings.DEBUG_DUMP_LOCATION )

  app.registerNamespace( '/', 'contractor.Auth' )
  app.registerNamespace( '/', 'contractor.BluePrint' )
  app.registerNamespace( '/', 'contractor.Site' )
  app.registerNamespace( '/', 'contractor.Survey' )
  app.registerNamespace( '/', 'contractor.Directory' )
  app.registerNamespace( '/', 'contractor.Utilities' )
  app.registerNamespace( '/', 'contractor.Building' )
  app.registerNamespace( '/', 'contractor.Foreman' )
  app.registerNamespace( '/', 'contractor.SubContractor' )
  app.registerNamespace( '/', 'contractor.PostOffice' )
  app.registerNamespace( '/', 'contractor.Records' )

  for plugin in plugin_list:
    try:
      app.registerNamespace( '/', plugin )
    except NoCINP:
      pass

  app.registerPathHandler( '/config/', config_handler )

  app.validate()

  return app
