from contractor.Building.models import Foundation, Structure
from contractor.Foreman.models import BaseJob, FoundationJob, StructureJob


def parse_script( script ):
  return {}

def createJob( script_name, structure=None, foundation=None, ):
  if structure is not None:
    job = StructureJob()
    job.site = structure.site
    job.structure = structure
    blueprint = structure.blueprint

  elif foundation is not None:
    job = FoundationJob()
    job.site = foundation.site
    job.foundation = foundation
    blueprint = foundation.blueprint

  else:
    raise Exception( 'Either structure or material must be specified' )

  try:
    script = blueprint.script_map[ script_name ]
  except KeyError:
    raise Exception( 'BluePrint "{0}" does not have a script named "{1}"'.format( blueprint, script_name ) )

  job.state = 'waiting'
  job.is_create = script_name == 'create'
  job.is_destroy = script_name == 'destroy'
  job.script_pos = [ 0 ]
  job.script_ast = parse_script( script )
  job.save()

def processJobs( site, max_jobs=10 ):
  if max_jobs > 100:
    max_jobs = 100

  # see if there are any located foundations that need to be prepared
  for foundation in Foundation.objects.filter( located_at__isnull=False, built_at__isnull=True ):
    try:
      FoundationJob.objects.get( foundation=foundation )
      continue # allready has a job, skip it
    except FoundationJob.DoesNotExist:
      pass

    createJob( 'create', foundation=foundation )

  # see if there are any structures on setup foundations to start
  for structure in Structure.objects.filter( built_at__isnull=True, auto_build=True, foundation__built_at__isnull=False ):
    try:
      StructureJob.objects.get( structure=structure )
      continue # allready has a job, skip it
    except StructureJob.DoesNotExist:
      pass

    createJob( 'create', structure=structure )

  # clean up completed jobs
  for job in BaseJob.objects.filter( site=site, state='done' ):
    job = job.realJob
    job.done()
    job.delete()

  # iterate over the curent jobs
  results = []
  for job in BaseJob.objects.filter( site=site, state='waiting' ).order_by( 'updated' ):
    job = job.realJob
    if len( results ) >= max_jobs:
      break

    print( job.script_pos )

    if job.script_pos[0] >= 10:
      job.state = 'done'
      job.save()
      continue

    # do stuff
    job.script_pos[0] += 1
    job.save()


  return results
