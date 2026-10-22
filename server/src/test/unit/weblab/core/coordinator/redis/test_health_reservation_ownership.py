"""Dependency-free Python 2 regression tests of the actual scheduler methods.

Extract only the methods to avoid starting coordinator threads or using live Redis.
The deployment smoke test additionally exercises the native public reservation flow.
"""
import ast
import json
import os
import unittest


class Stub(object):
    def __init__(self, **values):
        self.__dict__.update(values)


class Redis(object):
    def __init__(self):
        self.data = {}
        self.mutations = []

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.mutations.append(('set', key))
        self.data[key] = value

    def smembers(self, key):
        return set(['reservation'])

    def srem(self, key, value):
        self.mutations.append(('srem', key))
        return 1

    def hget(self, key, value):
        return 'ordered-reservation'

    def zadd(self, *args):
        self.mutations.append(('zadd', args[0]))


def load_methods():
    root = os.environ.get('WEBLAB_SOURCE_ROOT') or os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../../../..'))
    source = os.path.join(root, 'weblab/core/coordinator/redis/priority_queue_scheduler.py')
    constants = os.path.join(root, 'weblab/core/coordinator/redis/constants.py')
    namespace = {'json': json, 'Resource': Stub(parse=lambda value: value)}
    exec(compile(open(constants).read(), constants, 'exec'), namespace)
    tree = ast.parse(open(source).read(), source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PriorityQueueScheduler')
    methods = []
    for method in cls.body:
        if isinstance(method, ast.FunctionDef) and method.name in (
                'removing_current_resource_slot', 'confirm_experiment', 'finish_reservation'):
            method.decorator_list = []
            methods.append(method)
    module = ast.Module(body=methods)
    exec(compile(ast.fix_missing_locations(module), source, 'exec'), namespace)
    return namespace


N = load_methods()


class HealthOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.redis = Redis()
        self.released = []
        self.downgraded = []
        self.freed = []
        self.deleted = []
        self.resource = Stub(resource_type='basys3', resource_instance='board')
        self.scheduler = Stub(
            preserve_reservations_on_health_failure=True,
            resource_type_name='basys3', redis_maker=lambda: self.redis,
            _remove_expired_reservations=lambda: None,
            time_provider=Stub(get_time=lambda: 100),
            resources_manager=Stub(check_working=lambda value: False,
                                   release_resource=self.released.append),
            reservations_manager=Stub(downgrade_confirmation=self.downgraded.append),
            _clean_current_reservation=lambda value: ('lab', value, 'session', 'experiment'),
            _delete_reservation=self.deleted.append,
            confirmer=Stub(enqueue_free_experiment=lambda *args: self.freed.append(args)))
        self.key = N['WEBLAB_RESOURCE_RESERVATION_PQUEUE'] % ('basys3', 'reservation')

    def seed(self, status):
        self.redis.data[self.key] = json.dumps({
            N['ACTIVE_STATUS']: status, N['RESOURCE_INSTANCE']: 'board@basys3',
            N['LAB_SESSION_ID']: 'existing-session'})

    def remove(self):
        return N['removing_current_resource_slot'](self.scheduler, self.redis, self.resource)

    def test_confirmed_health_failure_preserves_ownership(self):
        self.seed(N['STATUS_RESERVED'])
        before = dict(self.redis.data)
        self.assertFalse(self.remove())
        self.assertEqual(before, self.redis.data)
        self.assertEqual([], self.redis.mutations + self.released + self.downgraded)

    def test_initializing_health_failure_preserves_ownership(self):
        self.seed(N['STATUS_WAITING_CONFIRMATION'])
        self.assertFalse(self.remove())
        self.assertEqual([], self.redis.mutations + self.released + self.downgraded)

    def test_repeated_health_failures_do_not_requeue(self):
        self.seed(N['STATUS_RESERVED'])
        for _ in range(5):
            self.remove()
        self.assertEqual([], self.redis.mutations)

    def test_owned_initialization_can_confirm_while_unhealthy(self):
        self.seed(N['STATUS_WAITING_CONFIRMATION'])
        N['confirm_experiment'](self.scheduler, 'reservation', Stub(id='new-session'), '{}', {})
        result = json.loads(self.redis.data[self.key])
        self.assertEqual(N['STATUS_RESERVED'], result[N['ACTIVE_STATUS']])
        self.assertEqual('new-session', result[N['LAB_SESSION_ID']])

    def test_unrelated_schedulers_keep_legacy_behavior(self):
        self.scheduler.preserve_reservations_on_health_failure = False
        self.seed(N['STATUS_RESERVED'])
        self.assertTrue(self.remove())
        self.assertEqual(['reservation'], self.downgraded)
        self.assertEqual([self.resource], self.released)

    def test_unrelated_schedulers_still_reject_unhealthy_confirmation(self):
        self.scheduler.preserve_reservations_on_health_failure = False
        self.seed(N['STATUS_WAITING_CONFIRMATION'])
        N['confirm_experiment'](self.scheduler, 'reservation', Stub(id='new-session'), '{}', {})
        self.assertEqual([], self.redis.mutations)

    def test_finish_still_enqueues_original_session_cleanup(self):
        self.seed(N['STATUS_RESERVED'])
        N['finish_reservation'](self.scheduler, 'reservation')
        self.assertEqual(['reservation'], self.deleted)
        self.assertEqual([('lab', 'reservation', 'session', 'experiment')], self.freed)


if __name__ == '__main__':
    unittest.main()
