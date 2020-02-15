import json
from cinp.orm_django import DjangoCInP as CInP

from contractor.Records.lib import collection


cinp = CInP( 'Records', '0.1' )


@cinp.staticModel( not_allowed_verb_list=[ 'LIST', 'GET', 'DELETE', 'CREATE', 'UPDATE' ] )
class Recorder():
  @cinp.action( return_type={ 'type': 'String', 'is_array': True }, paramater_type_list=[ { 'type': 'String', 'choice_list': [ 'Site', 'BluePrint', 'Structure', 'Foundation' ] }, 'String', 'String', 'Integer' ] )
  @staticmethod
  def query( group, query, fields='{}', max_results=100 ):
    db = collection( group )
    try:
      query = json.loads( query )
    except Exception as e:
      raise ValueError( 'query is not valid JSON: "{0}"'.format( e ) )

    try:
      fields = json.loads( fields )
    except Exception as e:
      raise ValueError( 'fields is not valid JSON: "{0}"'.format( e ) )

    if max_results < 0 or max_results > 10000:
      raise ValueError( 'max_results must be from 0 to 10000' )

    result = [ rec for rec in db.find( query, fields )[ :max_results ] ]  # TODO: detect if it's just ids, if so check return_objects and return the objects
    return result

  @cinp.action( return_type='String', paramater_type_list=[ { 'type': 'String', 'choice_list': [ 'Site', 'BluePrint', 'Structure', 'Foundation' ] }, 'String', 'Integer' ] )
  @staticmethod
  def queryObjects( group, query, max_results=100 ):
    db = collection( group )

    try:
      query = json.loads( query )
    except Exception as e:
      raise ValueError( 'query is not valid JSON: "{0}"'.format( e ) )

    if max_results < 0 or max_results > 10000:
      raise ValueError( 'max_results must be from 0 to 10000' )

    if group == 'Site':
      prefix = '/api/v1/Site/Site'
    elif group in ( 'BluePrint', 'StructureBluePrint', 'FoundationBluePrint' ):
      prefix = '/api/v1/BluePrint/BluePrint'
    elif group == 'Structure':
      prefix = '/api/v1/Building/Structure'
    elif group == 'Foundation':
      prefix = '/api/v1/Building/Foundation'

    result = prefix + ':' + ':'.join( [ rec[ '_id' ] for rec in db.find( query, {} )[ :max_results ] ] ) + ':'

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Recorder'
