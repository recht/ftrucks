"""
Simple ElasticSearch client.
"""

import urllib2
import logging
from server import rest

class ElasticSearch:
    """
    Initialize the client. This will also ensure that the proper index exists in ES.
    The index name is read from the config object under the ESINDEX key.
    """
    def __init__(self, config, type):
        hostname = config.get('ESHOST')
        index = config.get('ESINDEX')
        self.url = "http://{}/{}".format(hostname, index)
        logging.info("Ensuring index at %s", self.url)
        self.__ensure()
        self.type = type

    def add(self, id, document):
        """
        Add a document to the index.
        """
        rest.put("{}/{}/{}".format(self.url, self.type, id), document)

    def search(self, query):
        logging.debug("Searcing for %s", query)
        res = rest.post("{}/{}/_search".format(self.url, self.type), query)
        logging.debug("Search res: %s", res)
        return res

    def __ensure(self):
        try:
            res = rest.head(self.url)
        except urllib2.HTTPError, e:
            if e.code == 404:
                rest.put(self.url, {"mappings":
                                        {"truck": {
                                            "properties": {
                                                "location": {"type": "geo_point"},
                                                "updated": {"type": "date"}
                                            }
                                        }}})
            else:
                raise e

