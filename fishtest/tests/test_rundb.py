import unittest
import datetime

from fishtest.rundb import RunDb

import util

rundb = None
run_id_stc = None
run_id = None

class CreateRunDBTest(unittest.TestCase):

  def tearDown(self):
    rundb.runs.delete_many({'args.username': 'travis'})
    # Shutdown flush thread:
    rundb.stop()

  def test_10_create_run(self):
    global rundb, run_id, run_id_stc
    rundb = RunDb()
    # STC
    run_id_stc = rundb.new_run('master', 'master', 100000, '10+0.01', 'book', 10, 1, '', '',
                               username='travis', tests_repo='travis',
                               start_time=datetime.datetime.utcnow())
    run = rundb.get_run(run_id_stc)
    run['finished'] = True
    rundb.buffer(run, True)

    # LTC
    run_id = rundb.new_run('master', 'master', 100000, '150+0.01', 'book', 10, 1, '', '',
                           username='travis', tests_repo='travis',
                           start_time=datetime.datetime.utcnow())
    print(' ')
    print(run_id)
    run = rundb.get_run(run_id)
    print(run['tasks'][0])
    self.assertFalse(run['tasks'][0][u'active'])
    run['tasks'][0][u'active'] = True
    run['tasks'][0][u'worker_info'] = {
      'username': 'worker1', 'unique_key': 'travis', 'concurrency': 1}
    run['cores'] = 1

    print(util.find_run()['args'])

  def test_20_update_task(self):
    run = rundb.update_task(run_id, 0, {'wins': 1, 'losses': 1, 'draws': rundb.chunk_size-3,
                                      'crashes': 0, 'time_losses': 0}, 1000000, '', 'worker2')
    self.assertEqual(run, {'task_alive': False})
    run = rundb.update_task(run_id, 0, {'wins': 1, 'losses': 1, 'draws': rundb.chunk_size-3,
                                      'crashes': 0, 'time_losses': 0}, 1000000, '', 'worker1')
    self.assertEqual(run, {'task_alive': True})
    run = rundb.update_task(run_id, 0, {'wins': 1, 'losses': 1, 'draws': rundb.chunk_size-2,
                                      'crashes': 0, 'time_losses': 0}, 1000000, '', 'worker1')
    self.assertEqual(run, {'task_alive': False})

  def test_30_finish(self):
    run = rundb.get_run(run_id)
    run['finished'] = True
    rundb.buffer(run, True)

  def test_40_list_LTC(self):
    finished_runs= rundb.get_finished_runs(limit=3, ltc_only=True)[0]
    for run in finished_runs:
      print(run['args']['tc'])

  def test_90_delete_runs(self):
    for run in rundb.get_runs():
      if run['args']['username'] == 'travis' and not 'deleted' in run:
        print('del ')
        run['deleted'] = True
        run['finished'] = True
        for w in run['tasks']:
          w['pending'] = False
        rundb.buffer(run, True)


if __name__ == "__main__":
  unittest.main()
