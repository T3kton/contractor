import pytest
import pickle
import time
import threading

from django.db import transaction

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner
from contractor.Site.models import Site
from contractor.Foreman.models import BaseJob

from contractor.Foreman.lib import processJobs, jobResults


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

  return ( 'remote_func', 'the count "{0}"'.format( self.counter ) )


def _do_jobResults( job_id, cookie, data ):
  with transaction.atomic():
    jobResults( job_id, cookie, data )


def _do_processJobs( site, module_list, count ):
  global _process_job_results
  with transaction.atomic():
    _process_job_results = processJobs( site, module_list, count )

    while not _process_jobs_can_finish:
      time.sleep( 0.1 )


@pytest.mark.timeout( 20, method='thread' )
@pytest.mark.django_db( transaction=True )
def test_job_locking( mocker ):
  global _from_can_continue, _to_can_continue, _process_jobs_can_finish

  mocker.patch( 'contractor.tscript.runner_plugins_test.remote.fromSubcontractor', _fake_fromSubcontractor )
  mocker.patch( 'contractor.tscript.runner_plugins_test.remote.toSubcontractor', _fake_toSubcontractor )

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

  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': 1, 'module': 'testing', 'paramaters': 'the count "2"'}]

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
    jobResults( rc[0][ 'job_id' ], cookie, None )

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is False

  with transaction.atomic():
    cookie, rc = _stripcookie( processJobs( s, [ 'testing' ], 10 ) )
    assert rc == [{'function': 'remote_func', 'job_id': 1, 'module': 'testing', 'paramaters': 'the count "4"'}]

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState()[ 'state' ][2][1][ 'dispatched' ] is True

  # first test, running status check during a statesave
  _from_can_continue = False
  t = threading.Thread( target=_do_jobResults, args=( rc[0][ 'job_id' ], cookie, None ) )
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
    assert rc == [{'function': 'remote_func', 'job_id': 1, 'module': 'testing', 'paramaters': 'the count "5"'}]

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

      jobResults( rc[0][ 'job_id' ], cookie, None )

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
    assert rc == [{'function': 'remote_func', 'job_id': 1, 'module': 'testing', 'paramaters': 'the count "7"'}]

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

      t2 = threading.Thread( target=_do_jobResults, args=( rc[0][ 'job_id' ], cookie, None ) )  # jobResults should block b/c the record is locked
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
    assert rc == [{'function': 'remote_func', 'job_id': 1, 'module': 'testing', 'paramaters': 'the count "9"'}]

  with transaction.atomic():
    jobResults( rc[0][ 'job_id' ], cookie, 'adf' )

  with transaction.atomic():
    assert processJobs( s, [ 'testing' ], 10 ) == []

  with transaction.atomic():
    j = BaseJob.objects.get()
    assert j.state == 'queued'
    assert j.jobRunnerState() == {'cur_line': None, 'state': 'DONE'}
