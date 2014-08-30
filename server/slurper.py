import logging
import time
from server import rest
from server.elasticsearch import ElasticSearch

class Slurper:
    """
    Downloads and indexes food truck data from sfgov into ElasticSearch

    Attributes:
        es: an instance of ElasticSearch
    """

    def __init__(self, es):
        self.es = es

    def slurp(self):
        """
        Download and index data every 5 minutes.
        """
        while True:
            try:
                self.slurp_once()
            except Exception, e:
                logging.error("Got error while slurping", e)
            time.sleep(60*5)


    def slurp_once(self):
        """
        Download source data from sfgov and index it into ElasticSearch.
        """
        data = rest.get("https://data.sfgov.org/api/views/rqzj-sfat/rows.json?accessType=DOWNLOAD")
        for truck in self.__parse(data):
            if not 'Latitude' in truck or not 'Longitude' in truck:
                logging.debug("Skipping %s", truck)
                continue
            if not truck['Latitude'] or not truck['Longitude']:
                logging.debug("Skipping %s", truck)
                continue

            doc = dict()
            doc['location'] = {"lat": truck['Latitude'], "lon": truck['Longitude']}
            doc['applicant'] = truck['Applicant']
            doc['address'] = truck['Address']
            doc['items'] = truck['FoodItems']
            self.es.add(truck['id'], doc)

            logging.debug("Indexed %s", doc)


    def __parse(self, data):
        """
        Convert the sfgov data items to dicts so values can be accessed using names instead of indexes.
        """
        columns = []
        for field in data['meta']['view']['columns']:
            columns.append(field['name'])

        trucks = []
        for t in data['data']:
            truck = dict()
            pos = 0
            for column in columns:
                truck[column] = t[pos]
                pos += 1
            trucks.append(truck)

        return trucks





if __name__ == "__main__":

    Slurper().slurp(ElasticSearch("localhost:9200", "trucks"))
