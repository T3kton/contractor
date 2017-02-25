import pickle

from contractor.Building.models import Foundation, Structure
from contractor.Foreman.models import BaseJob, FoundationJob, StructureJob, cinp

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, Pause, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, ScriptError


RUNNER_MODULE_LIST = []

def createJob( script_name, target ):
  if isinstance( target, Structure ):
    job = StructureJob()
    job.structure = target

  elif isinstance( target, Foundation ):
    job = FoundationJob()
    job.foundation = target

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

  runner = Runner( target, parse( target.blueprint.get_script( script_name ) ) )
  for module in RUNNER_MODULE_LIST:
    runner.register_module( module )

  job.state = 'queued'
  job.script_name = script_name
  job.script_runner = pickle.dumps( runner )
  job.save()

  print( '**************** Created  Job "{0}" for "{1}"'.format( script_name, target ))

  return job.pk

def processJobs( site, max_jobs=10 ):
  if max_jobs > 100:
    max_jobs = 100

  # see if there are any planned foundatons that can be auto located
  for foundation in Foundation.objects.filter( located_at__isnull=True, built_at__isnull=True ):
    foundation = foundation.subclass
    if not foundation.can_auto_locate:
      continue

    foundation.setLocated()

  # see if there are any located foundations that need to be prepared
  for foundation in Foundation.objects.filter( located_at__isnull=False, built_at__isnull=True ):
    fondation = foundation.subclass
    try:
      FoundationJob.objects.get( foundation=foundation )
      continue # allready has a job, skip it
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', target=foundation )

  # see if there are any structures on setup foundations to start
  for structure in Structure.objects.filter( built_at__isnull=True, auto_build=True, foundation__built_at__isnull=False ):
    try:
      StructureJob.objects.get( structure=structure )
      continue # allready has a job, skip it
    except StructureJob.DoesNotExist:
      pass

    createJob( 'create', target=structure )

  # clean up completed jobs
  for job in BaseJob.objects.filter( site=site, state='done' ):
    print( '_________________________ job "{0}" done!'.format(  job ) )
    job = job.realJob
    job.done()
    job.delete()

  # iterate over the curent jobs
  results = []
  for job in BaseJob.objects.filter( site=site, state='queued' ).order_by( 'updated' ):
    job = job.realJob

    runner = pickle.loads( job.script_runner )
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

    if runner.aborted:
      job.state = 'aborted'

    if runner.done:
      job.state = 'done'

    if job.state == 'queued':
      result = runner.to_contractor()
      if result is not None:
        job.state = 'waiting'
        results.append( result )

    job.status = runner.status
    print( '____________ job "{0}"   state: "{1}"   progress: "{2}"    message: "{3}"'.format( job, job.state, job.progress, job.message ) )
    job.script_runner = pickle.dumps( runner )
    job.save()

    if len( results ) >= max_jobs:
      break

  return results
