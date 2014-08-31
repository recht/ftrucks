"""
The main backend server.

This exposes basic static resources as well as a websocket endpoint.
"""
from threading import Thread

from flask import Flask, render_template, redirect, request
from flask.ext.socketio import SocketIO, emit
from server.elasticsearch import ElasticSearch
from slurper import Slurper
from server import bus
from server.bus.buswatcher import BusWatcher
from gevent import monkey
import logging

monkey.patch_all()

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
app.logger.setLevel(logging.DEBUG)
socketio = SocketIO(app)

es = ElasticSearch(app.config, 'truck')
watcher = BusWatcher(app.config.get('WATCH'))

if app.config.get('SLURP'):
    s = Slurper(es)
    thread = Thread(target=s.slurp)
    thread.start()

@app.route('/')
def index():
    """
    Get the main static html page for the app.
    """
    return redirect('/static/index.html')

@socketio.on('connect')
def connected(msg = None):
    """
    When a client connects, it should emit a connect event.
    Once connected, the client will receive an 'init' event that contains a list of active routes.
    """
    if msg is not None:
        busses = bus.get_busses()
        emit('init', {'busses': busses})

@socketio.on('disconnect')
def disconnected():
    """
    On client disconnect we remove any watchers for that client.
    """
    print 'disconnected'
    watcher.remove_watch(request)

@socketio.on('new-location')
def new_location(msg):
    """
    Indicate that a client has selected new locations.
    Once processed, the client will receive a 'new-trucks' event back that lists which trucks are available around the
    selected locations.
    :param msg: An array of elements that contain 'lat' and 'lon' attributes.

    """
    if len(msg) == 0:
        return

    qs = map(lambda m: {'geo_distance': {
        'distance': '200m',
        'location': {
            'lat': m['lat'],
            'lon': m['lon']
        }
    }}, msg)
    res = es.search({'query': {
        'filtered': {
            'filter': {
                'or': qs
            }
        }
    }, 'size': 500
    })
    hits = map(lambda hit: hit['_source'], res['hits']['hits'])
    emit('new-trucks', hits)

@socketio.on('bus-selected')
def bus_selected(msg):
    """
    Indicate that a client has selected a specific route to watch.
    When locations have been found for the selected route, a 'bus-located' event will be sent to the client. This event
    will be emitted every time locations change for the selected route.
    :param msg: A structure that contains a 'route' property. The value should be one of the values returned earlier by
    the init event.
    """
    watcher.add_watch(request, msg['route'])
