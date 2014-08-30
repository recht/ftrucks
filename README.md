Food Truck/Bus Map
==================

This implements a food truck service based on the location of Muni vehicle locations in SF. It can either show food trucks
within 100 meters of a specific location (as identified by clicking on the map) or within 100 meters of an active Muni vehicle.

There's no automatic geolocation as that's a little hard to test out when you're outside SF. Instead, you can choose a
Muni route, and the map will automatically update the nearby food trucks based on the real-time location of the vehicle.

The project was implemented as a full-stack project, although time prevented deep work on the frontend part.

Running the project
-------------------
It's the normal Python thing - I use virtualenv.
```
virtualenv trucks
. trucks/bin/activate

pip install -r requirements.txt
python start.py
```

Frontend Implementation
-----------------------

The frontend is implemented using AngularJS for the very basic data binding, OpenLayers 3 for the map and SocketIO for
websocket communication. AngularJS was mainly chosen because of the very limited interactions between logic and UI (only
the route dropdown is accessed through AngularJS) and because it's what I have the most experience with.

Unfortunately, OpenLayers 3 is fairly new and the documentation is a little bit lacking, so especially the marker click
events can sometimes be a little off. Also, just updating markers on the map apparently doesn't update the UI so right now
all markers are removed and then added again on updates, which arguably is not the best approach.

Had I had more time, I would have moved a lot of the Javascript code out of the single trucks.js file and into Angular service
classes and only keep the event binding in the main controller class.

Backend implementation
----------------------
The backend is implemented in Python using Flask and Flask-SocketIO. I have no prior experience with Flask, and I mainly
chose it because I wanted to try implementing a client/server solution based mainly on Websockets instead of normal REST
(of which I have done plenty). In this regard, Flask-SocketIO looked very simple compared to for example Tornado or
similar.

The backend uses two data sources: The food cart list from sfgov.org and the real-time vehicle information from nextbus.com.

Since the food cart list is not very large, the backend just downloads it periodically and indexes the required information
into ElasticSearch. This is of course a shortcut, but I believe the approach is viable for even quite large files, esp. since
the data doesn't really change very often.

Vehicle information from nextbus.com is used when you select a route on the map. When that happens, the route will be
registered on the server and a watch process will poll the nextbus API for changes. If changes come in, they will be pushed
back to the client over the Websocket connection.

Scheduling runs in normal Python threads. It could be run through a worker queue instead, but for this purpose a simple
thread makes OK sense. However, proper error handling inside the thread is missing as the thread will die if an exception
occurs, which then requires a restart.

Tests are implemented as a mix of Flask unit tests and plain unit tests based on the context. Some of the tests use mocking
to avoid calling external resources. All tests are written in basic BDD style and can be executed using
```python -m unittest discover```.

