from threading import Thread
import time
from server import bus


class BusWatcher:
    """
    This continuously polls the NextBus API for location updates and emits events on changes.
    """
    def __init__(self, start):
        self.requests = {}
        self.last_times = {}
        if start:
            thread = Thread(target=self.watch)
            thread.start()

    def add_watch(self, request, route):
        """
        Start watching a specific route and send changes to the channel specified.
        """
        self.remove_watch(request)
        if not route in self.requests:
            self.requests[route] = set()
        self.requests[route].add(request.namespace)
        self.update_locations()

    def remove_watch(self, request):
        """
        Stop watching any route for a specific channel.
        """
        for route in self.requests:
            self.requests[route].discard(request.namespace)

    def watch(self):
        while True:
            time.sleep(5)
            self.update_locations()

    def update_locations(self):
        """
        Loop through all watches and poll for changes.
        """
        for route in self.requests:
            requests = self.requests[route]
            if len(requests) == 0:
                continue

            locations, last_time = bus.get_locations(route, self.last_times.get(route))
            if last_time != self.last_times.get(route):
                self.last_times[route] = last_time
                for request in requests:
                    request.emit('bus-located', locations)
