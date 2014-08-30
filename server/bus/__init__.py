from server import rest
import urllib

def get_busses():
    """
    Get a list of routes currently operated by SF Muni.
    :return: A list of dicts with route and name attributes.
    """
    res = rest.get('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni')

    routes = map(lambda route: {'route': route.attrib.get('tag'), 'name': route.attrib.get('title')}, res.route)
    return routes

def get_locations(route, lastTime = None):
    """
    Get the list of active vehicles for a specific route.
    :param lastTime: Either 0 or the timestamp returned by a previous call to this function.
    :return: A tuple of (locations, timestamp). Locations is a list of dicts with id, lat, lon, heading, route attributes.
    """
    if not lastTime:
        lastTime = 0
    query = urllib.urlencode({'command': 'vehicleLocations', 'a': 'sf-muni', 'r': route, 't': lastTime})
    res = rest.get('http://webservices.nextbus.com/service/publicXMLFeed?{}'.format(query))
    try:
        locations = map(lambda v: {
            'id': v.attrib.get('id'),
            'lat': v.attrib.get('lat'),
            'lon': v.attrib.get('lon'),
            'heading': v.attrib.get('heading'),
            'route': v.attrib.get('routeTag')
        }, res.vehicle)
        return locations, res.lastTime.attrib.get('time')
    except AttributeError, e:
        # this happens when the response is empty
        return [], lastTime

if __name__ == '__main__':
    get_busses()
