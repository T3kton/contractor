import pickle
from django.core.exceptions import ObjectDoesNotExist

from contractor.Building.models import Foundation, Structure, Dependency
from contractor.Foreman.runner_plugins.building import ConfigPlugin, FoundationPlugin, ROFoundationPlugin, StructurePlugin, ROStructurePlugin
from contractor.Foreman.models import BaseJob, FoundationJob, StructureJob, DependencyJob, JobLog, ForemanException
from contractor.PostOffice.lib import registerEvent

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, Pause, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, ScriptError


RUNNER_MODULE_LIST = []

#  Job Can Create Matrix
#                                    Associated Asset
#                   | Structure | Structure | Structure | Foundation | Foundation | Foundation | Foundation | Dependency | Dependency | Dependency |
#  Job Type         |  Planned  |   Built   |  Has Job  |   Planned  |   Located  |    Built   |   Has Job  |  Planned   |   Built    |   Has Job  |
# --------------------------------------------------------------------------------------------------------------------------------------------------
# Structure Create  |    *            B           J           *            *            *             1           .             .           .      |
# Structure Destroy |    D            *           J           I            I            *             2           .             .           .      |
# Foundation Create |    .            .           .           *            *            B             J           *             *           1      |
# Foundation Destroy|    .            .           .           D            D            *             J           I             *           2      |
# Dependency Create |    *            *           1           .            .            .             .           *             B           J      |
# Dependency Destroy|    I            *           2           .            .            .             .           D             *           J      |
# *all* Utility     |    D            *           D           D            D            *             D           .             .           .      |
# --------------------------------------------------------------------------------------------------------------------------------------------------
# NOTE: Dependency can depend on Dependency the same way it depends on Structure, so that (dependency-structure) block needs to apply to both (dependency and structure)
#  * -> yes
#  1 -> yes if the existing job is a build job
#  2 -> yes if the existing job is a destroy job
#  . -> no linkage
#  B -> Allready Built Error
#  D -> Not Built Error
#  J -> Has  Job  Error
#  I -> Dependant not in Correct state Error

# TODO: make sure a dependency can't create a job for a structure with a job, or a structure that is not built
# TODO: can't create a foundation destroy job when the structure has a job

JOB_LOOKUP_MAP = { 'Foundation': 'foundationjob', 'Structure': 'structurejob', 'Dependency': 'dependencyjob' }
DEPENDENCY_LOOKUP_MAP = { 'Foundation': ( 'dependency', ), 'Structure': ( 'foundation', ), 'Dependency': ( 'structure', 'dependency' ) }


def _target_class( target ):
  if isinstance( target, Foundation ):
    return 'Foundation'
  elif isinstance( target, ( Structure, Dependency ) ):
    return target.__class__.__name__
  else:
    raise ForemanException( 'INVALID_TARGET', 'target must be a Structure, Foundation, or Dependency' )


def createJob( script_name, target, creator ):
  if not creator:
    raise ForemanException( 'INVALID_CREATOR', 'creator is blank' )

  target_class = _target_class( target )

  if isinstance( target, Dependency ) and script_name not in ( 'create', 'destroy' ):
    raise ForemanException( 'INVALID_SCRIPT', 'Dependency Job can only have a create or destroy script_name' )

  try:
    if getattr( target, JOB_LOOKUP_MAP[ target_class ] ) is not None:
      raise ForemanException( 'JOB_EXISTS', 'target has an existing job' )
  except ObjectDoesNotExist:
    pass

  if script_name == 'create':
    if target.state == 'built':
      raise ForemanException( 'ALLREADY_BUILT', 'target allready built' )

    for item in DEPENDENCY_LOOKUP_MAP[ target_class ]:
      try:
        target_dependency = getattr( target, item )
      except ObjectDoesNotExist:
        target_dependency = None

      if target_dependency is not None:
        try:
          dependency_job = getattr( target_dependency, JOB_LOOKUP_MAP[ _target_class( target_dependency ) ] )
          if dependency_job.script_name != 'create':
            raise ForemanException( 'JOB_EXISTS', 'target\'s dependency has an existing non-create job' )
        except ObjectDoesNotExist:
          pass

  elif script_name == 'destroy':
    if target.state != 'built':
      raise ForemanException( 'NOT_BUILT', 'target not built' )

    for item in DEPENDENCY_LOOKUP_MAP[ target_class ]:
      try:
        target_dependency = getattr( target, item )
      except ObjectDoesNotExist:
        target_dependency = None

      if target_dependency is not None:
        try:
          dependency_job = getattr( target_dependency, JOB_LOOKUP_MAP[ _target_class( target_dependency ) ] )
          if dependency_job.script_name != 'destroy':
            raise ForemanException( 'JOB_EXISTS', 'target\'s dependency has an existing non-destroy job' )
        except ObjectDoesNotExist:
          pass

        if target_dependency.state != 'built':  # this one should not happen, but just in case
          raise ForemanException( 'NOT_BUILT', 'the supporting target to the target is not built' )

  else:
    if target.state != 'built':
      raise ForemanException( 'NOT_BUILT', 'target not built' )

  blueprint = target.blueprint

  obj_list = []
  if isinstance( target, Structure ):
    job = StructureJob()
    job.structure = target
    obj_list.append( ROFoundationPlugin( target.foundation ) )
    obj_list.append( StructurePlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  elif isinstance( target, Foundation ):
    job = FoundationJob()
    job.foundation = target
    obj_list.append( FoundationPlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  elif isinstance( target, Dependency ):
    job = DependencyJob()
    job.dependency = target
    structure = None
    if target.script_structure:
      structure = target.script_structure
    else:
      structure = target.structure
    # TODO: need a plugin to bring in the target foundation
    obj_list.append( ROFoundationPlugin( structure.foundation ) )
    obj_list.append( ROStructurePlugin( structure ) )
    obj_list.append( ConfigPlugin( structure ) )

  job.site = target.site

  script = blueprint.get_script( script_name )
  if script is None:
    script = '# empty place holder'

  runner = Runner( parse( script ) )
  for module in RUNNER_MODULE_LIST:
    runner.registerModule( module )

  for module in ( 'contractor.Foreman.runner_plugins.dhcp', ):
    runner.registerModule( module )

  for obj in obj_list:
    runner.registerObject( obj )

  job.state = 'waiting'
  job.script_name = script_name
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  JobLog.fromJob( job, True, creator )

  return job.pk


def processJobs( site, module_list, max_jobs=10 ):
  if max_jobs > 100:
    max_jobs = 100

  # how to know if something can just be located, for now, if it has a complex and the complex is up and running
  # then we can auto locate.  The question is, should we go back to the foundation haveing a can_auto_locate
  # flag again, do we need that kind of detail?
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=True, built_at__isnull=True ):
    foundation = foundation.subclass
    if foundation.complex.state == 'built':
      foundation.setLocated()

  # start waiting jobs
  for job in BaseJob.objects.select_for_update().filter( site=site, state='waiting' ):
    job = job.realJob
    if job.can_start:
      job.state = 'queued'
      job.full_clean()
      job.save()

  # clean up completed jobs
  for job in BaseJob.objects.select_for_update().filter( site=site, state='done' ):
    job = job.realJob
    job.done()
    if isinstance( job, StructureJob ):
      registerEvent( job.structure, job=job )

    elif isinstance( job, FoundationJob ):
      registerEvent( job.foundation, job=job )

    JobLog.fromJob( job, False, '*INTERNAL*' )

    job.delete()

  # iterate over the curent jobs
  results = []
  for job in BaseJob.objects.select_for_update().filter( site=site, state='queued' ).order_by( 'updated' ):
    job = job.realJob
    runner = pickle.loads( job.script_runner )

    if runner.aborted:
      job.state = 'aborted'
      job.full_clean()
      job.save()
      continue

    if runner.done:
      job.state = 'done'
      job.full_clean()
      job.save()
      continue

    try:
      job.message = runner.run()

    except Pause as e:
      job.state = 'paused'
      job.message = str( e )[ 0:1024 ]

    except ExecutionError as e:
      job.state = 'error'
      job.message = str( e )[ 0:1024 ]

    except ( UnrecoverableError, ParamaterError, NotDefinedError, ScriptError ) as e:
      job.state = 'aborted'
      job.message = str( e )[ 0:1024 ]

    except Exception as e:
      job.state = 'aborted'
      job.message = 'Unknown Runtime Exception ({0}): "{1}"'.format( type( e ).__name__, str( e ) )[ 0:1024 ]

    if job.state == 'queued':
      task = runner.toSubcontractor( module_list )
      if task is not None:
        task.update( { 'job_id': job.pk } )
        results.append( task )

    job.status = runner.status
    job.script_runner = pickle.dumps( runner )
    job.full_clean()
    job.save()

    if len( results ) >= max_jobs:
      break

  return results


# TODO: we will need some kind of job record locking, so only one thing can happen at a time, ie: rolling back when things are still comming in,
#   trying to handler.run() when fromsubContractor is happening, pretty much, anything the runner is unpickled, nothing else should  happen to
#   the job till it is pickled and saved
def jobResults( job_id, cookie, data ):
  try:
    job = BaseJob.objects.select_for_update().get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ForemanException( 'JOB_NOT_FOUND', 'Error saving job results: "Job Not Found"' )

  job = job.realJob
  runner = pickle.loads( job.script_runner )
  result = runner.fromSubcontractor( cookie, data )
  if result != 'Accepted':  # it wasn't valid/taken, no point in saving anything
    raise ForemanException( 'INVALID_RESULT', 'Error saving job results: "{0}"'.format( result ) )

  job.status = runner.status
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  return result


def jobError( job_id, cookie, msg ):
  try:
    job = BaseJob.objects.select_for_update().get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ForemanException( 'JOB_NOT_FOUND', 'Error setting job to error: "Job Not Found"' )

  job = job.realJob
  runner = pickle.loads( job.script_runner )
  if cookie != runner.contractor_cookie:  # we do our own out of bad cookie check b/c this type of error dosen't need to be propagated to the script runner
    raise ForemanException( 'BAD_COOKIE', 'Error setting job to error: "Bad Cookie"' )

  job.message = msg[ 0:1024 ]
  job.state = 'error'
  job.full_clean
  job.save()
