from unittest import TestCase
from server import rest

class RestTest(TestCase):

    def test_get_returns_parsed_json(self):
        res = rest.get('http://ip.jsontest.com/')
        print res
        self.assertTrue('ip' in res)

    def test_get_returns_parsed_xml(self):
        res = rest.get('http://central.maven.org/maven2/junit/junit/4.8.1/junit-4.8.1.pom')
        self.assertEqual('4.0.0', res.modelVersion)
