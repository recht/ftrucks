from flask.ext.testing import TestCase
from flask import url_for

from . import app, socketio
from mock import Mock, patch
import server
import unittest

class TruckTest(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def test_index_redirects_to_static_file(self):
        response = self.client.get(url_for('index'))
        self.assert_redirects(response, '/static/index.html')

class SocketTest(unittest.TestCase):

    def setUp(self):
        self.client = socketio.test_client(app)
        self.client.get_received()

    def test_connecting_sends_back_list_of_routes(self):
        mock_bus = Mock()
        mock_bus.get_busses.return_value = [{'id': '1'}]
        with patch.object(server, 'bus', mock_bus):
            self.client.emit('connect', {})
            emitted = self.client.get_received()
            self.assertEquals(emitted[0]['args'][0]['busses'], [{'id': '1'}])

    def test_on_new_location_trucks_are_looked_up_by_coordinates(self):
        mock_es = Mock(name='es')
        mock_es.search.return_value = {"hits": {"hits": []}}
        with patch.object(server, 'es', mock_es):
            self.client.emit('new-location', [{'lat': 0, 'lon': 0}])
            emitted = self.client.get_received()
            self.assertEquals(0, len(emitted[0]['args'][0]))
            self.assertTrue(mock_es.search.called)

    def test_selecting_route_adds_watch(self):
        mock_watch = Mock()
        with patch.object(server, 'watcher', mock_watch):
            with patch.object(server, 'request', Mock()):
                self.client.emit('bus-selected', {'route': '1'})
                self.assertTrue(mock_watch.add_watch.called)