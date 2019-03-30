from cinp.orm_django import DjangoCInP as CInP

from contractor.Records.lib import connect


cinp = CInP( 'Records', '0.1' )


@cinp.staticModel( not_allowed_verb_list=[ 'LIST', 'GET', 'DELETE', 'CREATE', 'UPDATE' ] )
class Recorder():
  @cinp.action( return_type='Map', paramater_type_list=[ 'String', 'String', 'Boolean' ] )
  @staticmethod
  def query( collection, query, return_objects=False ):
    db = connect()
    if collection == 'Site':
      db = db.site
    elif collection in ( 'StructureBluePrint', 'FoundationBluePrint' ):
      db = db.blueprint
    elif collection == 'Structure':
      db = db.structure
    elif collection == 'Foundation':
      db = db.foundation
    else:
      raise ValueError( 'Unknown Collection "{0}"'.format( collection ) )

    result = db.find( query )  # TODO: detect if it's just ids, if so check return_objects and return the objects

    return result
