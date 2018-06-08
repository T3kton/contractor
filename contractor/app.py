from cinp.server_werkzeug import WerkzeugServer

from contractor.User.models import getUser
from contractor.lib.config_handler import handler as config_handler


def get_app( debug ):
  app = WerkzeugServer( root_path='/api/v1/', root_version='0.9', debug=debug, get_user=getUser, cors_allow_list=[ '*' ] )

  app.registerNamespace( '/', 'contractor.User' )
  app.registerNamespace( '/', 'contractor.BluePrint' )
  app.registerNamespace( '/', 'contractor.Site' )
  app.registerNamespace( '/', 'contractor.Utilities' )
  app.registerNamespace( '/', 'contractor.Building' )
  app.registerNamespace( '/', 'contractor.Foreman' )
  app.registerNamespace( '/', 'contractor.SubContractor' )
  app.registerNamespace( '/', 'contractor.PostOffice' )

  app.registerNamespace( '/', 'contractor_plugins.Manual' )
  app.registerNamespace( '/', 'contractor_plugins.VirtualBox' )

  app.registerPathHandler( '/config/', config_handler )

  app.validate()

  return app
