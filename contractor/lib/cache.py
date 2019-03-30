from pymongo import MongoClient

from django.conf import settings

from contractor.lib.config import getConfig


_mongo_db = None


def _connect():
  global _mongo_db
  if _mongo_db is not None:
    return _mongo_db

  _mongo_db = MongoClient( settings.MONGO_HOST ).contractor
  return _mongo_db


def _collection( db, target ):
  if target.__class__.__name__ == 'Site':
    return db.site
  elif target.__class__.__name__ in ( 'StructureBluePrint', 'FoundationBluePrint' ):
    return db.blueprint
  elif target.__class__.__name__ == 'Structure':
    return db.structure
  elif 'Foundation' in [ i.__name__ for i in target.__class__.__mro__ ]:
    return db.foundation
  else:
    raise ValueError( 'Unable to located collection for "{0}"' )


def updateConfig( target ):
  collection = _collection( _connect(), target )

  item = getConfig( target )
  for i in ( '__contractor_host', '__pxe_template_location', '__pxe_location' ):  # these are the same everywhere
    del item[i]

  key = { '_id': target.pk }

  collection.update( key, item, upsert=True )


def removeConfig( target ):
  collection = _collection( _connect(), target )

  query = { '_id': target.pk }
  collection.remove( query )


def post_save_callback( **kwargs ):
  updateConfig( kwargs[ 'instance' ] )
