import pytest
import pickle
import time
import threading

from django.db import transaction

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner
from contractor.Site.models import Site
from contractor.Foreman.models import BaseJob  # , FoundationJob, StructureJob, DependencyJob
from contractor.Building.models import Foundation, Structure, Dependency
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint  # , BluePrintScript, Script

from contractor.Foreman.lib import processJobs, jobResults, createJob


class TestUser():
  username = 'tester'


def _stripcookie( item_list ):
  for item in item_list:
    cookie = item[ 'cookie' ]
    del item[ 'cookie' ]

  return cookie, item_list


_from_can_continue = True
_to_can_continue = True
_process_jobs_can_finish = True
_process_job_results = None


def _fake_fromSubcontractor( self, data ):
  while not _from_can_continue:
    time.sleep( 0.1 )

  self.state = data


def _fake_toSubcontractor( self ):
  while not _to_can_continue:
    time.sleep( 0.1 )

  return ( 'remote_func', 'the fake count "{0}"'.format( self.counter ) )


def _do_jobResults( job_id, cookie, data ):
  with transaction.atomic():
    jobResults( job_id, cookie, data )


def _do_processJobs( site, module_list, count ):
  global _process_job_results
  with transaction.atomic():
    _process_job_results = processJobs( site, module_list, count )

    while not _process_jobs_can_finish:
      time.sleep( 0.1 )


def fake_canSetState( self, job=None ):
  return True


@pytest.mark.django_db( transaction=True )
def test_job_saving_loading( mocker ):
  s = Site( name='test', description='test' )
  s.full_clean()
  s.save()

  runner = Runner( parse( 'begin( expected_time=0:10, max_time=0:10 )\ndelay( seconds=1 )\ntesting.remote()\nend' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  job = BaseJob( site=s )
  job.state = 'queued'
  job.script_name = 'test'
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  job = BaseJob.objects.get()
  runner = pickle.loads( job.script_runner )
  job.message = runner.run()
  job.status = runner.status
  runner.toSubcontractor( [ 'testing' ] )
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  time.sleep( 1 )

  job = BaseJob.objects.get()
  runner = pickle.loads( job.script_runner )
  job.message = runner.run()
  job.status = runner.status
  runner.toSubcontractor( [ 'testing' ] )
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()

  time.sleep( 1 )

  job = BaseJob.objects.get()
  runner = pickle.loads( job.script_runner )
  job.message = runner.run()
  job.status = runner.status
  runner.toSubcontractor( [ 'testing' ] )
  job.script_runner = pickle.dumps( runner )
  job.full_clean()
  job.save()


@pytest.mark.timeout( 60, method='thread' )
@pytest.mark.django_db( transaction=True )
def test_job_locking( mocker ):
  global _from_can_continue, _to_can_continue, _process_jobs_can_finish

  mocker.patch( 'contractor.tscript.runner_plugins_test.Remote.fromSubcontractor', _fake_fromSubcontractor )
  mocker.patch( 'contractor.tscript.runner_plugins_test.Remote.toSubcontractor', _fake_toSubcontractor )

  with transaction.atomic():
    s = Site( name='test', description='test' )
    s.full_clean()
    s.save()

    runner = Runner( parse( 'testing.remote()' ) )
    runner.registerModule( 'contractor.tscript.runner_plugins_test' )
    job = BaseJob( site=s )
    job.state = 'queued'
    job.script_name = 'test'
    job.script_runner = pickle.dumps( runner )
    job.full_clean()
    job.save()

    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState() == {'cur_line': 0, 'state': []}

  _to_can_continue = True
  _from_can_continue = True

  with transaction.atomic():
    assert processJobs( s, [], 10 ) == []

    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  job_id = None

  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    job_id = rc[0][ 'job_id' ]
    assert rc == [{'function': 'remote_func', 'job_id': job_id, 'module': 'testing', 'paramaters': 'the fake count "2"'}]

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  with transaction.atomic():
    assert processJobs( s, [ 'testing' ], 10 ) == []

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  with transaction.atomic():
    jobResults( job_id, cookie, None )

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': job_id, 'module': 'testing', 'paramaters': 'the fake count "4"'}]

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  # first test, running status check during a statesave
  _from_can_continue = False
  t = threading.Thread( target=_do_jobResults, args=( job_id, cookie, None ) )
  try:
    t.start()
    time.sleep( 0.5 )

    with transaction.atomic():
      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

    time.sleep( 0.5 )
    _from_can_continue = True
    t.join()

  except Exception as e:
    _from_can_continue = True
    t.join()
    raise e

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  # now we test intrupting the job checking with results, first during a slow toSubcontractor
  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': job_id, 'module': 'testing', 'paramaters': 'the fake count "5"'}]

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  _to_can_continue = False
  _process_jobs_can_finish = True
  t = threading.Thread( target=_do_processJobs, args=( s, [ 'testing' ], 10 ) )
  try:
    t.start()
    time.sleep( 0.5 )

    with transaction.atomic():
      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

      jobResults( job_id, cookie, None )

      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

    time.sleep( 0.5 )
    _to_can_continue = True
    t.join()

  except Exception as e:
    _to_can_continue = True
    t.join()
    raise e

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  # then just before the transaction commits
  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': job_id, 'module': 'testing', 'paramaters': 'the fake count "7"'}]

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  _to_can_continue = True
  _process_jobs_can_finish = False
  t = threading.Thread( target=_do_processJobs, args=( s, [ 'testing' ], 10 ) )
  try:
    t.start()
    time.sleep( 0.5 )

    with transaction.atomic():
      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

      t2 = threading.Thread( target=_do_jobResults, args=( job_id, cookie, None ) )  # jobResults should block b/c the record is locked
      t2.start()

      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

    time.sleep( 0.5 )
    _process_jobs_can_finish = True

    t2.join()
    with transaction.atomic():
      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

    t.join()
    with transaction.atomic():
      j = BaseJob.objects.get()
      assert j.state == 'queued'
      assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  except Exception as e:
    _process_jobs_can_finish = True
    t.join()
    raise e

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  # and finish up the job
  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': job_id, 'module': 'testing', 'paramaters': 'the fake count "9"'}]

  with transaction.atomic():
    jobResults( job_id, cookie, 'adf' )

  with transaction.atomic():
    assert processJobs( s, [ 'testing' ], 10 ) == []

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState() == {'cur_line': None, 'state': 'DONE'}


@pytest.mark.django_db()
def test_job_create():
  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', si, TestUser() )
  assert str( execinfo.value.code ) == 'INVALID_TARGET'


@pytest.mark.django_db()
def test_foundation_job_create():  # TODO: should also do tests depending on a Dependency
  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  assert createJob( 'create', f, TestUser() ) is not None
  assert f.state == 'planned'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', f, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setLocated()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  with pytest.raises( ValueError ) as execinfo:
    createJob( 'other', f, TestUser()  )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  assert createJob( 'create', f, TestUser() ) is not None
  assert f.state == 'located'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', f, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )

  f.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', f, TestUser() )
  assert str( execinfo.value.code ) == 'ALLREADY_BUILT'
  assert f.state == 'built'

  assert createJob( 'other', f, TestUser() ) is not None
  assert f.state == 'built'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', f, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )

  assert createJob( 'destroy', f, TestUser() ) is not None
  assert f.state == 'built'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )


@pytest.mark.django_db()
def test_foundation_with_structure_job_create():
  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  f.setDestroyed()
  assert createJob( 'create', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setLocated()
  assert createJob( 'create', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', f, TestUser() )
  assert str( execinfo.value.code ) == 'ALLREADY_BUILT'

  f.setDestroyed()
  s.setDestroyed()
  assert createJob( 'create', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setLocated()
  s.setBuilt()
  assert createJob( 'create', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setBuilt()
  s.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', f, TestUser() )
  assert str( execinfo.value.code ) == 'ALLREADY_BUILT'

  s.setDestroyed()
  f.setBuilt()
  assert createJob( 'destroy', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  f.setLocated()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  f.setDestroyed()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  s.setBuilt()
  f.setBuilt()
  assert createJob( 'destroy', f, TestUser() ) is not None
  f.foundationjob.delete()
  f = Foundation.objects.get( pk=f.pk )
  s.setDestroyed()
  f.setLocated()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  f.setDestroyed()
  s.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', f, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'


@pytest.mark.django_db()
def test_structure_job_create():  # TODO: test structures with dependency
  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', s, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', s, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  assert createJob( 'create', s, TestUser() ) is not None
  assert s.state == 'planned'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', s, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.structurejob.delete()
  s = Structure.objects.get( pk=s.pk )
  f.setBuilt()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', s, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', s, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  s.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', s, TestUser() )
  assert str( execinfo.value.code ) == 'ALLREADY_BUILT'
  assert s.state == 'built'

  assert createJob( 'other', s, TestUser() ) is not None
  assert s.state == 'built'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', s, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.structurejob.delete()
  s = Structure.objects.get( pk=s.pk )

  assert createJob( 'destroy', s, TestUser() ) is not None
  assert s.state == 'built'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', s, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.structurejob.delete()
  s = Structure.objects.get( pk=s.pk )

  s.setDestroyed()
  f.setLocated()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', s, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  # test job type checking
  s.setDestroyed()
  f.setDestroyed()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )
  assert createJob( 'create', f, TestUser() ) is not None
  assert createJob( 'create', s, TestUser() ) is not None
  s.structurejob.delete()
  f.foundationjob.delete()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )

  s.setDestroyed()
  f.setBuilt()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )
  assert createJob( 'other', f, TestUser() ) is not None
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', s, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )

  s.setBuilt()
  f.setBuilt()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )
  assert createJob( 'destroy', f, TestUser() ) is not None
  assert createJob( 'destroy', s, TestUser() ) is not None
  s.structurejob.delete()
  f.foundationjob.delete()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )

  s.setBuilt()
  f.setBuilt()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )
  assert createJob( 'other', f, TestUser() ) is not None
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', s, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  f.foundationjob.delete()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )


@pytest.mark.django_db()
def test_dependency_job_create():
  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  f.setBuilt()

  d = Dependency()
  d.structure = s
  d.link = 'soft'
  d.full_clean()
  d.save()

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', d, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  with pytest.raises( Exception ) as execinfo:
    createJob( 'other', d, TestUser() )
  assert str( execinfo.value.code ) == 'INVALID_SCRIPT'

  assert createJob( 'create', d, TestUser() ) is not None
  assert d.state == 'planned'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', d, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.setBuilt()
  d.dependencyjob.delete()
  d = Dependency.objects.get( pk=d.pk )

  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', d, TestUser() )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  d.setBuilt()
  with pytest.raises( Exception ) as execinfo:
    createJob( 'create', d, TestUser() )
  assert str( execinfo.value.code ) == 'ALLREADY_BUILT'
  assert d.state == 'built'

  assert createJob( 'destroy', d, TestUser() ) is not None
  assert d.state == 'built'
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', d, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  d.dependencyjob.delete()
  d = Dependency.objects.get( pk=d.pk )

  # test job type checking
  d.setDestroyed()
  s.setDestroyed()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )
  assert createJob( 'create', s, TestUser() ) is not None
  assert createJob( 'create', d, TestUser() ) is not None
  d.dependencyjob.delete()
  s.structurejob.delete()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )

  d.setDestroyed()
  s.setBuilt()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )
  assert createJob( 'other', s, TestUser() ) is not None
  with pytest.raises( ValueError ) as execinfo:
    createJob( 'create', d, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.structurejob.delete()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )

  d.setBuilt()
  s.setBuilt()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )
  assert createJob( 'destroy', s, TestUser() ) is not None
  assert createJob( 'destroy', d, TestUser() ) is not None
  d.dependencyjob.delete()
  s.structurejob.delete()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )

  d.setBuilt()
  s.setBuilt()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )
  assert createJob( 'other', s, TestUser() ) is not None
  with pytest.raises( ValueError ) as execinfo:
    createJob( 'destroy', d, TestUser() )
  assert str( execinfo.value.code ) == 'JOB_EXISTS'
  s.structurejob.delete()
  d = Dependency.objects.get( pk=d.pk )
  s = Structure.objects.get( pk=s.pk )


@pytest.mark.django_db()
def test_can_start_create( mocker ):
  mocker.patch( 'contractor.Building.models.Foundation._canSetState', fake_canSetState )  # disable the job checking
  mocker.patch( 'contractor.Building.models.Structure._canSetState', fake_canSetState )
  mocker.patch( 'contractor.Building.models.Dependency._canSetState', fake_canSetState )

  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  createJob( 'create', f, TestUser() )
  assert f.foundationjob.can_start is False

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  createJob( 'create', s, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False

  d = Dependency()
  d.structure = s
  d.link = 'soft'
  d.full_clean()
  d.save()

  createJob( 'create', d, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False

  d2 = Dependency()
  d2.dependency = d
  d2.link = 'soft'
  d2.full_clean()
  d2.save()

  createJob( 'create', d2, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setLocated()
  assert f.foundationjob.can_start is True
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is True
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  s.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is True
  assert d2.dependencyjob.can_start is False

  d.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is True

  f.setDestroyed()
  s.setDestroyed()
  d.setDestroyed()
  d2.setDestroyed()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  d = Dependency.objects.get( pk=d.pk )
  d.foundation = f
  d.full_clean()
  d.save()

  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setLocated()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  d.setBuilt()
  d2 = Dependency.objects.get( pk=d2.pk )
  assert f.foundationjob.can_start is True
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is True


@pytest.mark.django_db()
def test_can_start_destroy( mocker ):
  mocker.patch( 'contractor.Building.models.Foundation._canSetState', fake_canSetState )  # disable the job checking
  mocker.patch( 'contractor.Building.models.Structure._canSetState', fake_canSetState )
  mocker.patch( 'contractor.Building.models.Dependency._canSetState', fake_canSetState )

  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  f.setBuilt()

  createJob( 'destroy', f, TestUser() )
  assert f.foundationjob.can_start is True

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  s.setBuilt()

  createJob( 'destroy', s, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is True

  d = Dependency()
  d.structure = s
  d.link = 'soft'
  d.full_clean()
  d.save()

  d.setBuilt()

  createJob( 'destroy', d, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is True

  d2 = Dependency()
  d2.dependency = d
  d2.link = 'soft'
  d2.full_clean()
  d2.save()

  d2.setBuilt()

  createJob( 'destroy', d2, TestUser() )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is True

  d2.setDestroyed()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is True
  assert d2.dependencyjob.can_start is False

  d.setDestroyed()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  s.setDestroyed()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setDestroyed()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  d2.setDestroyed()
  d.setBuilt()
  s.setBuilt()
  f.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is True
  assert d2.dependencyjob.can_start is False

  d = Dependency.objects.get( pk=d.pk )
  d.foundation = f
  d.full_clean()
  d.save()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setDestroyed()
  s.setBuilt()  # setting foundation to destoyed, destroys the structure, which destroys the dependency
  d.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  f.setBuilt()
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False
  assert d2.dependencyjob.can_start is False

  d2.dependencyjob.delete()
  d2.setDestroyed()
  f = Foundation.objects.get( pk=f.pk )
  s = Structure.objects.get( pk=s.pk )
  d = Dependency.objects.get( pk=d.pk )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is False

  d.dependencyjob.delete()
  d.setDestroyed()
  f = Foundation.objects.get( pk=f.pk )
  s = Structure.objects.get( pk=s.pk )
  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is True

  s.structurejob.delete()
  s.setDestroyed()
  s = Structure.objects.get( pk=s.pk )
  f = Foundation.objects.get( pk=f.pk )
  assert f.foundationjob.can_start is True

  s.delete()  # setting foundation.structure to None
  f = Foundation.objects.get( pk=f.pk )
  assert f.foundationjob.can_start is True


@pytest.mark.django_db()
def test_can_start_mixed( mocker ):
  mocker.patch( 'contractor.Building.models.Foundation._canSetState', fake_canSetState )  # disable the job checking
  mocker.patch( 'contractor.Building.models.Structure._canSetState', fake_canSetState )
  mocker.patch( 'contractor.Building.models.Dependency._canSetState', fake_canSetState )

  si = Site()
  si.name = 'test'
  si.description = 'test'
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation()
  f.locator = 'test'
  f.site = si
  f.blueprint = fb
  f.full_clean()
  f.save()

  sb = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  s = Structure()
  s.foundation = f
  s.hostname = 'test'
  s.site = si
  s.blueprint = sb
  s.full_clean()
  s.save()

  d = Dependency()
  d.structure = s
  d.link = 'soft'
  d.full_clean()
  d.save()

  f.setBuilt()
  s.setDestroyed()

  createJob( 'create', s, TestUser() )
  createJob( 'destroy', f, TestUser() )

  assert f.foundationjob.can_start is False
  assert s.structurejob.can_start is True

  f.foundationjob.delete()
  s.structurejob.delete()
  f = Foundation.objects.get( pk=f.pk )
  s = Structure.objects.get( pk=s.pk )

  d = Dependency.objects.get( pk=d.pk )
  d.foundation = f
  d.full_clean()
  d.save()

  d.setBuilt()
  s.setBuilt()
  d.setDestroyed()
  d = Dependency.objects.get( pk=d.pk )

  createJob( 'create', d, TestUser() )
  createJob( 'destroy', s, TestUser() )

  assert s.structurejob.can_start is False
  assert d.dependencyjob.can_start is True

  s.structurejob.delete()
  d.dependencyjob.delete()
  s = Structure.objects.get( pk=s.pk )
  d = Dependency.objects.get( pk=d.pk )

  s.setDestroyed()
  d.setBuilt()
  f.setLocated()
  s = Structure.objects.get( pk=s.pk )

  createJob( 'create', f, TestUser() )
  with pytest.raises( Exception ) as execinfo:
    createJob( 'destroy', d, TestUser()  )
  assert str( execinfo.value.code ) == 'NOT_BUILT'

  assert f.foundationjob.can_start is True

  f.foundationjob.delete()
  d = Dependency.objects.get( pk=d.pk )
  f = Foundation.objects.get( pk=f.pk )
