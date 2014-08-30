from unittest import TestCase
from buswatcher import BusWatcher
import buswatcher
from mock import Mock, patch


class BusTest(TestCase):

    def setUp(self):
        self.watch = BusWatcher(False)
        self.mock_bus = Mock()
        self.mock_bus.get_locations.return_value = ([], 0)

    def test_adding_same_request_twice_only_adds_one_watch(self):
        req = DummyRequest()
        with patch.object(buswatcher, 'bus', self.mock_bus):
            self.watch.add_watch(req, '1')
            self.watch.add_watch(req, '1')

            self.assertTrue('1' in self.watch.requests)
            self.assertEquals(1, len(self.watch.requests['1']))

    def test_removing_request_removes_it_from_all_routes(self):
        req = DummyRequest()
        with patch.object(buswatcher, 'bus', self.mock_bus):
            self.watch.add_watch(req, '1')
            self.watch.add_watch(req, '2')

            self.watch.remove_watch(req)

            self.assertEquals(0, len(self.watch.requests['1']))
            self.assertEquals(0, len(self.watch.requests['2']))

    def test_removing_unknown_request_does_not_fail(self):
        self.watch.remove_watch(DummyRequest())


    def test_updating_locations_requests_locations_only_once_per_route(self):
        with patch.object(buswatcher, 'bus', self.mock_bus):
            self.watch.add_watch(DummyRequest(), '1')
            self.watch.add_watch(DummyRequest(), '1')
            self.watch.add_watch(DummyRequest(), '2')
            self.mock_bus.reset_mock()

            self.watch.update_locations()

            self.assertEquals(2, self.mock_bus.get_locations.call_count)

    def test_updating_locations_emits_bus_located_event(self):
        with patch.object(buswatcher, 'bus', self.mock_bus):
            req = DummyRequest()
            self.watch.add_watch(req, '1')

            self.watch.update_locations()

            req.namespace.emit.assert_called_once_with('bus-located', [])





class DummyRequest:
    def __init__(self):
        self.namespace = Mock()
