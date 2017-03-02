from cinp.orm_django import DjangoCInP as CInP

from contractor.Foreman.lib import processJobs, jobResults

cinp = CInP( 'SubContractor', '0.1' )

# these are only for subcontractor to talk to, thus some of the job_id short cuts
@cinp.staticModel()  #TODO: move to  Foreman?
class Dispatch():
  def __init__( self ):
    super().__init__()

  @cinp.action( return_type={ 'type': 'Map', 'is_array': True }, paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' }, { 'type': 'String', 'is_array': True }, 'Integer' ] )
  @staticmethod
  def getJobs( site='/api/v1/Site/Site:site1:', module_list=[ 'virtualbox' ], max_jobs=10 ):
    result = processJobs( site, module_list, max_jobs )
    print( '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "{0}"'.format( result ))
    return result

  @cinp.action( return_type='String', paramater_type_list=[ 'Integer', 'String', 'Map' ] )
  @staticmethod
  def jobResults( job_id, cookie, data ):
    print( '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< "{0}" "{1}" "{2}"'.format( job_id, cookie, data ) )
    return jobResults( job_id, cookie, data )

  @cinp.action( paramater_type_list=[ 'Integer', 'String', 'String' ] )
  @staticmethod
  def jobError( job_id, cookie, msg ):
    print( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! "{0}" "{1}" "{2}"'.format( job_id, cookie, msg ) )
    jobError( job_id, cookie, msg )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True
