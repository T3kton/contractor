import pickle

from contractor.Building.models import Foundation, Structure
from contractor.Foreman.models import BaseJob, FoundationJob, StructureJob, cinp
from contractor.lib.config import getConfig

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, Pause, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, ScriptError


RUNNER_MODULE_LIST = []


def createJob( script_name, target ):
  obj_list = []
  if isinstance( target, Structure ):
    job = StructureJob()
    job.structure = target
    obj_list.append( StructureFoundationPlugin( target.foundation ) )
    obj_list.append( StructurePlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  elif isinstance( target, Foundation ):
    job = FoundationJob()
    job.foundation = target
    obj_list.append( FoundationPlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  else:
    raise ValueError( 'target must be a Structure or Foundation' )

  if script_name == 'create':
    if target.state == 'built':
      raise ValueError( 'target allready built' )

    if isinstance( target, Foundation ):
      if target.state != 'located':
        raise ValueError( 'can not do create job until Foundation is located' )

  elif script_name == 'destroy':
    if target.state != 'built':
      raise ValueError( 'can only destroy built targets' )

  else:
    if isinstance( target, Foundation ) and target.state != 'located':
      raise ValueError( 'can only run utility jobs on located Foundations' )

  job.site = target.site

  runner = Runner( parse( target.blueprint.get_script( script_name ) ) )
  for module in RUNNER_MODULE_LIST:
    runner.registerModule( module )
  for obj in obj_list:
    runner.registerObject( obj )

  job.state = 'queued'
  job.script_name = script_name
  job.script_runner = pickle.dumps( runner )
  job.save()

  print( '**************** Created  Job "{0}" for "{1}"'.format( script_name, target ))

  return job.pk


def processJobs( site, module_list, max_jobs=10 ):
  if max_jobs > 100:
    max_jobs = 100

  # see if there are any planned foundatons that can be auto located
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=True, built_at__isnull=True ):
    foundation = foundation.subclass
    if not foundation.can_auto_locate:
      continue

    foundation.setLocated()

  # see if there are any located foundations that need to be prepared
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=False, built_at__isnull=True ):
    fondation = foundation.subclass
    try:
      FoundationJob.objects.get( foundation=foundation )
      continue # allready has a job, skip it
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', target=foundation )

  # see if there are any structures on setup foundations to start
  for structure in Structure.objects.filter( site=site, built_at__isnull=True, auto_build=True, foundation__built_at__isnull=False ):
    try:
      StructureJob.objects.get( structure=structure )
      continue # allready has a job, skip it
    except StructureJob.DoesNotExist:
      pass

    createJob( 'create', target=structure )

  # clean up completed jobs
  for job in BaseJob.objects.filter( site=site, state='done' ):
    print( '_________________________ job "{0}" done!'.format( job ) )
    job = job.realJob
    job.done()
    job.delete()

  # iterate over the curent jobs
  results = []
  for job in BaseJob.objects.filter( site=site, state='queued' ).order_by( 'updated' ):
    job = job.realJob
    print( '~~~~~~~~~~~~~~~~~~ "{0}"'.format( job ))

    runner = pickle.loads( job.script_runner )

    if runner.aborted:
      job.state = 'aborted'
      job.save()
      continue

    if runner.done:
      job.state = 'done'
      job.save()
      continue

    try:
      job.message = runner.run()

    except Pause as e:
      job.state = 'paused'
      job.message = str( e )

    except ExecutionError as e:
      job.state = 'error'
      job.message = str( e )

    except ( UnrecoverableError, ParamaterError, NotDefinedError, ScriptError ) as e:
      job.state = 'aborted'
      job.message = str( e )

    except Exception as e:
      job.state = 'aborted'
      job.message = 'Unknown Runtime Exception ({0}): "{1}"'.format( typ( e ).__name__, str( e ) )

    if job.state == 'queued':
      task = runner.toSubcontractor( module_list )
      if task is not None:
        task.update( { 'job_id': job.pk } )
        results.append( task )

    job.status = runner.status
    print( '____________ job "{0}"   state: "{1}"   progress: "{2}"    message: "{3}"'.format( job, job.state, job.progress, job.message ) )
    job.script_runner = pickle.dumps( runner )
    job.save()

    if len( results ) >= max_jobs:
      break

  return results


#TODO: we will need some kind of job record locking, so only one thing can happen at a time, ie: rolling back when things are still comming in,
#   trying to handler.run() when fromsubContractor is happening, pretty much, anything the runner is unpickled, nothing else should  happen to
#   the job till it is pickled and saved
def jobResults( job_id, cookie, data ):
  try:
    job = BaseJob.objects.get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ValueError( 'Error saving job results: "Job Not Found"' )

  job =  job.realJob
  runner = pickle.loads( job.script_runner )
  result = runner.fromSubcontractor( cookie, data )
  if result != 'Accepted': # it wasn't valid/taken, no point in saving anything
    raise ValueError( 'Error saving job results: "{0}"'.format( result ) )

  job.status = runner.status
  print( '----------------- job "{0}"   state: "{1}"   progress: "{2}"    message: "{3}"'.format( job, job.state, job.progress, job.message ) )
  job.script_runner = pickle.dumps( runner )
  job.save()

  return result


def jobError( job_id, cookie, msg ):
  try:
    job = BaseJob.objects.get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ValueError( 'Error setting job to error: "Job Not Found"' )

  job =  job.realJob
  runner = pickle.loads( job.script_runner )
  if cookie != runner.contractor_cookie: # we do our own out of bad cookie check b/c this type of error dosen't need to be propagated to the script runner
    raise ValueError( 'Error setting job to error: "Bad Cookie"' )

  job.message = msg
  job.state = 'error'
  job.save()


class ConfigPlugin( object ): # this is purley Read Only, if wiring is needed have to set it to the structure/foundation's config_values, and figure out a way to reload
  TSCRIPT_NAME = 'config'

  def __init__( self, target ):
    super().__init__()
    if isinstance( target, dict ):
      self.config = target
    else:
      self.config = getConfig( target )

  def getValues( self ):
    result = {}
    for key in self.config:
      result[ key ] = ( lambda key=key: self.config[ key ], None )

    return result

  def getFunctions( self ):
    result = {}

    return result

  def __reduce__( self ):
    return ( self.__class__, ( self.config, ) )


class FoundationPlugin( object ):
  TSCRIPT_NAME = 'foundation'

  def __init__( self, foundation ): # most of the time all that is needed is the locator, so we are going to cache that and only go get the object if other than locator is needed
    super().__init__()
    self._dirty_list = []
    if isinstance( foundation, tuple ):
      self._foundation = None
      self.foundation_class = foundation[0]
      self.foundation_pk = foundation[1]
      self.foundation_locator = foundation[2]

    else:
      self._foundation = foundation.subclass
      self.foundation_class = self._foundation.__class__
      self.foundation_pk = foundation.pk
      self.foundation_locator = foundation.locator

    self.value_map = self.foundation_class.getTscriptValues( True )
    self.function_map = self.foundation_class.getTscriptFunctions()

  @property
  def foundation( self ):
    if self._foundation is None:
      self._foundation = self.foundation_class.objects.get( pk=self.foundation_pk )

    return self._foundation

  def _setValue( self, name, val ):
    setter = self.value_map[ name ][1]
    setter( self.foundation, val )
    self._dirty_list.append( name )

  def getValues( self ):
    result = {}
    for key in self.value_map:
      getter = self.value_map[ key ][0]
      setter = self.value_map[ key ][1]
      if setter is not None:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), lambda val, name=key: self._setValue( name, val ) )
      else:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), None )

    result[ 'locator' ] = ( lambda: self.foundation_locator, None )

    return result

  def getFunctions( self ):
    result = {}
    for key in self.function_map:
      builder = self.function_map[ key ]
      result[ key ] = lambda builder=builder: builder( self.foundation )

    return result

  def __reduce__( self ):
    if self._foundation is not None and self._dirty_list:
      self._foundation.save( update_fields=self._dirty_list )

    return ( self.__class__, ( ( self.foundation_class, self.foundation_pk, self.foundation_locator ), ) )


class StructureFoundationPlugin( FoundationPlugin ): # ie: read only foundation
  def __init__( self, foundation ):
    super().__init__( foundation )
    # the same as Foundation plugin, except we want read onlyt value_map, so replace value_map with this and call it good
    self.value_map = self.foundation_class.getTscriptValues( False )


class StructurePlugin( object ): # ie: structure with some settable attributes, 'config' is structures (with the foundation merged in of course)
  TSCRIPT_NAME = 'structure'

  def __init__( self, structure ):
    super().__init__()
    self.structure = structure

  def getValues( self ):
    result = {}
    result[ 'hostname' ] = ( lambda: self.structure.hostname, None )

    return result

  def getFunctions( self ):
    result = {}

    return result
