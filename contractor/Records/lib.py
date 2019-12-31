from pymongo import MongoClient
from django.conf import settings

from contractor.lib.config import getConfig, mergeValues


_mongo_db = None


def _connect():
  global _mongo_db
  if _mongo_db is not None:
    return _mongo_db

  _mongo_db = MongoClient( settings.MONGO_HOST ).contractor
  return _mongo_db


def collection( target ):
  db = _connect()

  if isinstance( target, str ):
    if target == 'Site':
      return db.site
    elif target in ( 'BluePrint', 'StructureBluePrint', 'FoundationBluePrint' ):
      return db.blueprint
    elif target == 'Structure':
      return db.structure
    elif target == 'Foundation':
      return db.foundation

    raise ValueError( 'Unknown Collection type "{0}"'.format( target ) )

  else:
    if target.__class__.__name__ == 'Site':
      return db.site
    elif target.__class__.__name__ in ( 'StructureBluePrint', 'FoundationBluePrint' ):
      return db.blueprint
    elif target.__class__.__name__ == 'Structure':
      return db.structure
    elif 'Foundation' in [ i.__name__ for i in target.__class__.__mro__ ]:
      return db.foundation

    raise ValueError( 'Unable to located collection for "{0}"'.format( target ) )


def prepConfig( config ):
  if isinstance( config, dict ):
    for key in list( config.keys() ):
      if not isinstance( key, str ):
        config[ str( key ) ] = config[ key ]
        del config[ key ]
        key = str( key )

      elif any( i in key for i in ( 'password', 'token', 'secret' ) ):  # this should match subcontractor/subcontractor/handler.py - _hideify_internal
        del config[ key ]
        continue

      config[ key ] = prepConfig( config[ key ] )

  elif isinstance( config, ( list, tuple ) ):
    config = [ prepConfig( i ) for i in config ]

  return config


def updateRecord( target ):
  db = collection( target )

  item = mergeValues( getConfig( target ) )
  for i in ( '__contractor_host', '__pxe_template_location', '__pxe_location' ):  # these are the same everywhere
    del item[i]

  key = { '_id': target.pk }

  prepConfig( item )
  db.update( key, item, upsert=True )


def removeRecord( target ):
  db = collection( target )

  query = { '_id': target.pk }
  db.remove( query )


def post_save_callback( **kwargs ):
  updateRecord( kwargs[ 'instance' ] )


def post_delete_callback( **kwargs ):
  removeRecord( kwargs[ 'instance' ] )
