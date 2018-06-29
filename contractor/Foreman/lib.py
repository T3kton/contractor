import pickle
from django.db.models import Q

from contractor.Building.models import Foundation, Structure, Dependancy
from contractor.Foreman.runner_plugins.building import ConfigPlugin, FoundationPlugin, ROFoundationPlugin, StructurePlugin, ROStructurePlugin
from contractor.Foreman.models import BaseJob, FoundationJob, StructureJob, DependancyJob
from contractor.PostOffice.lib import registerEvent

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, Pause, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, ScriptError


RUNNER_MODULE_LIST = []

# TODO: make sure a dependancy can't create a job for a structure with a job, or a structure that is not built


def createJob( script_name, target ):
  if isinstance( target, Dependancy ) and script_name not in ( 'create', 'destroy' ):
    raise ValueError( 'Dependancy Job can only have a create or destroy script_name' )

  if script_name == 'create':
    if target.state == 'built':
      raise ValueError( 'target allready built' )

    if isinstance( target, Foundation ):
      if target.state != 'located':
        raise ValueError( 'can not do create job until Foundation is located' )

    elif isinstance( target, Dependancy ):
      script_name = target.create_script_name
      if script_name is None:
        target.setBuilt()
        return None

  elif script_name == 'destroy':
    if target.state != 'built':
      raise ValueError( 'can only destroy built targets' )

    if isinstance( target, Dependancy ):
      script_name = target.destroy_script_name
      if script_name is None:
        target.setDestroyed()
        return None

  else:
    if isinstance( target, Foundation ) and target.state != 'located':
      raise ValueError( 'Can Only run Scripts Job on Located Foundations' )

  obj_list = []
  if isinstance( target, Structure ):
    job = StructureJob()
    job.structure = target
    obj_list.append( ROFoundationPlugin( target.foundation ) )
    obj_list.append( StructurePlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  elif isinstance( target, Foundation ):
    structure = target.attached_structure
    if structure is not None:
      try:
        StructureJob.objects.get( structure=structure )
        raise ValueError( 'Structure associated with this Foundation has a job' )
      except StructureJob.DoesNotExist:
        pass

    job = FoundationJob()
    job.foundation = target
    obj_list.append( FoundationPlugin( target ) )
    obj_list.append( ConfigPlugin( target ) )

  elif isinstance( target, Dependancy ):
    if target.dependancy is not None:
      if target.dependancy.state != 'built':
        raise ValueError( 'Can not start Dependancy job until Dependancy is built')
    else:
      if target.structure.state != 'built':
        raise ValueError( 'Can not start Dependancy job until Structure is built')

    job = DependancyJob()
    job.dependancy = target
    structure = None
    if target.script_structure:
      structure = target.script_structure
    else:
      structure = target.structure
    # TODO: need a plugin to bring in the target foundation
    obj_list.append( ROFoundationPlugin( structure.foundation ) )
    obj_list.append( ROStructurePlugin( structure ) )
    obj_list.append( ConfigPlugin( structure ) )

  else:
    raise ValueError( 'target must be a Structure, Foundation, or Dependancy' )

  job.site = target.site
  blueprint = target.blueprint

  script = blueprint.get_script( script_name )
  if script is None:
    if script_name == 'create':
      target.setBuilt()
    elif script_name == 'destroy':
      target.setDestroyed()

    return None

  runner = Runner( parse( script ) )
  for module in RUNNER_MODULE_LIST:
    runner.registerModule( module )

  for module in ( 'contractor.Foreman.runner_plugins.dhcp', ):
    runner.registerModule( module )

  for obj in obj_list:
    runner.registerObject( obj )

  job.state = 'queued'
  job.script_name = script_name
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  print( '**************** Created  Job "{0}" for "{1}"'.format( script_name, target ))

  return job.pk


# auto job creation checklist  TODO: add the dependancy info in this checklist
# 1 - Any Foundation that can be auto located, if locating is possible, it can be
#         done without foundation dependancies
#         (located_at is null, built_at is also null)
#   ---> Set To located
# 2 - Any Located Foundation without dependancies
#         ( located_at is not null, built_at is null, depenancies is null)
#   ---> Create a Foundation Build job
# 3 - Any Located Foundation with dependancies that are build
#         ( located_at is not null, built_at is null, all depenancies build_at is not null)
#   ---> Create Foundation Build Job
# 4 - Any Structure which not built and is auto_build and and foundation is built_at
#         ( built_at is null, foundation_built_at is not null, auto_build is True)
#   ---> Create Structure Build Job
#
# NOTE:  Foundations that rely on a Complex should check the complex's build state
#        when evaluating auto_locate, ie: use auto_locate as a "dependancy" check on
#        the complex.

def processJobs( site, module_list, max_jobs=10 ):
  if max_jobs > 100:
    max_jobs = 100

  # see if there are any planned dependancies who's structures are done
  for dependancy in Dependancy.objects.filter( built_at__isnull=True ).filter(
                                      Q( structure__built_at__isnull=False ) |
                                      Q( dependancy__built_at__isnull=False )
                                    ).filter(
                                      Q( foundation__site=site ) |
                                      Q( foundation__isnull=True, script_structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, dependancy__structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, structure__site=site )
                                    ):
    try:
      DependancyJob.objects.get( dependancy=dependancy )
      continue  # allready has a job, skip it
    except DependancyJob.DoesNotExist:
      pass

    createJob( 'create', target=dependancy )  # createJob will map 'create' to the create_script_name

  # see if there are any planned foundatons that can be auto located - TODO: Can something with a non built dependancy auto-locate, I think for now yes.
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=True, built_at__isnull=True ):
    foundation = foundation.subclass
    if not foundation.can_auto_locate:
      continue

    foundation.setLocated()

  # see if there are any located foundations that need to be prepared, with out dependancies
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=False, built_at__isnull=True, dependancy__isnull=True ):
    foundation = foundation.subclass
    try:
      FoundationJob.objects.get( foundation=foundation )
      continue  # allready has a job, skip it
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', target=foundation )

  # see if there are any located foundations that need to be prepared, with completed dependancies
  for foundation in Foundation.objects.filter( site=site, located_at__isnull=False, built_at__isnull=True, dependancy__built_at__isnull=False ):
    # TODO: check to see if the depency has a job that can be started <-------------

    foundation = foundation.subclass
    try:
      FoundationJob.objects.get( foundation=foundation )
      continue  # allready has a job, skip it
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', target=foundation )

  # see if there are any structures on setup foundations to start
  for structure in Structure.objects.filter( site=site, built_at__isnull=True, auto_build=True, foundation__built_at__isnull=False ):
    try:
      StructureJob.objects.get( structure=structure )
      continue  # allready has a job, skip it
    except StructureJob.DoesNotExist:
      pass

    try:
      FoundationJob.objects.get( foundation=structure.foundation )
      continue  # the foundation is doing something, structure shoud not do anything till is is done
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', target=structure )

  # clean up completed jobs
  for job in BaseJob.objects.filter( site=site, state='done' ):
    print( '_________________________ job "{0}" done!'.format( job ) )
    job = job.realJob
    job.done()
    if isinstance( job, StructureJob ):
      registerEvent( job.structure, job )

    elif isinstance( job, FoundationJob ):
      registerEvent( job.foundation, job )

    job.delete()

  # iterate over the curent jobs
  results = []
  for job in BaseJob.objects.filter( site=site, state='queued' ).order_by( 'updated' ):
    job = job.realJob
    print( '~~~~~~~~~~~~~~~~~~ "{0}"'.format( job ))

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
    print( '____________ job "{0}"   state: "{1}"   progress: "{2}"    message: "{3}"'.format( job, job.state, job.progress, job.message ) )
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
    job = BaseJob.objects.get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ValueError( 'Error saving job results: "Job Not Found"' )

  job = job.realJob
  runner = pickle.loads( job.script_runner )
  result = runner.fromSubcontractor( cookie, data )
  if result != 'Accepted':  # it wasn't valid/taken, no point in saving anything
    raise ValueError( 'Error saving job results: "{0}"'.format( result ) )

  job.status = runner.status
  print( '----------------- job "{0}"   state: "{1}"   progress: "{2}"    message: "{3}"'.format( job, job.state, job.progress, job.message ) )
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  return result


def jobError( job_id, cookie, msg ):
  try:
    job = BaseJob.objects.get( pk=job_id )
  except BaseJob.DoesNotExist:
    raise ValueError( 'Error setting job to error: "Job Not Found"' )

  job = job.realJob
  runner = pickle.loads( job.script_runner )
  if cookie != runner.contractor_cookie:  # we do our own out of bad cookie check b/c this type of error dosen't need to be propagated to the script runner
    raise ValueError( 'Error setting job to error: "Bad Cookie"' )

  job.message = msg[ 0:1024 ]
  job.state = 'error'
  job.full_clean
  job.save()
