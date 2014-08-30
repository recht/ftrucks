from threading import Thread

from flask import Flask, render_template, redirect, request
from flask.ext.socketio import SocketIO, emit
from server.elasticsearch import ElasticSearch
from slurper import Slurper
from server import bus
from server.bus.buswatcher import BusWatcher


app = Flask(__name__)
app.config.from_object('config.BaseConfig')
socketio = SocketIO(app)

es = ElasticSearch(app.config, 'truck')
watcher = BusWatcher(app.config.get('WATCH'))

if app.config.get('SLURP'):
    s = Slurper(es)
    thread = Thread(target=s.slurp)
    thread.start()

@app.route('/')
def index():
    return redirect('/static/index.html')

@socketio.on('connect')
def connected(msg = None):
    if msg is not None:
        busses = bus.get_busses()
        emit('init', {'busses': busses})

@socketio.on('disconnect')
def disconnected():
    print 'disconnected'
    watcher.remove_watch(request)

@socketio.on('new-location')
def new_location(msg):
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
    watcher.add_watch(request, msg['route'])
