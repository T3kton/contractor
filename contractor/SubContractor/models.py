from cinp.orm_django import DjangoCInP as CInP

from contractor.Foreman.lib import processJobs

cinp = CInP( 'SubContractor', '0.1' )


@cinp.staticModel()  #TODO: move to  Foreman?
class Dispatch():
  def __init__( self ):
    super().__init__()

  @cinp.action( return_type={ 'type': 'Map', 'is_array': True }, paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' }, 'Integer' ] )
  @staticmethod
  def getJobs( site, max_jobs=10 ):
    result = processJobs( site, max_jobs )
    print( '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "{0}"'.format( result ))
    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True
