import copy
import datetime
import json
import mock
from mock import patch
import unittest

import gocardless
from gocardless.resources import Resource

class TestResource(Resource):
    endpoint = "/testendpoint/:id"

    def __init__(self, attrs, client):
        attrs = create_mock_attrs(attrs)
        Resource.__init__(self, attrs, client)

class TestSubResource(Resource):
    endpoint = "/subresource/:id"

class OtherTestSubResource(Resource):
    endpoint = "/subresource2/:id"

def create_mock_attrs(to_merge):
    """
    Creats an attribute set for creating a resource from, 
    includes the basic created, modified and id keys. Merges
    that with to_merge
    """
    attrs = {
            "created_at":"2012-04-18T17:53:12Z", 
            "id":"1"}
    attrs.update(to_merge)
    return attrs

class ResourceTestCase(unittest.TestCase):

    def test_endpoint_declared_by_class(self):
        resource = TestResource({"id":"1"}, None)
        self.assertEqual(resource.get_endpoint(), "/testendpoint/1")

    def test_resource_attributes(self):
        attrs = {"key1":"one",
                "key2":"two",
                "key3":"three",
                "id":"1"}
        res = TestResource(attrs.copy(), None)
        for key, value in attrs.items():
            self.assertEqual(getattr(res, key), value)

    def test_resource_created_at_modified_at_are_dates(self):
        created = datetime.datetime.strptime('2012-04-18T17:53:12Z',\
                "%Y-%m-%dT%H:%M:%SZ")
        attrs = create_mock_attrs({"created_at":'2012-04-18T17:53:12Z',
               "id":"1"})
        res = TestResource(attrs, None)
        self.assertEqual(res.created_at, created)

class ResourceSubresourceTestCase(unittest.TestCase):

    def setUp(self):
        self.resource = TestResource({"sub_resource_uris":       
            {"test_sub_resources":
                "https://gocardless.com/api/v1/merchants/WOQRUJU9OH2HH1/bills?\
                        source_id=1580",
             "other_test_sub_resources": "aurl"}, 
            "id":"1"},
            None)

    def test_resource_lists_subresources(self):
        self.assertTrue(hasattr(self.resource, "get_test_sub_resources"))
        self.assertTrue(callable(getattr(self.resource, "get_test_sub_resources")))

    def test_resource_subresource_returns_subresource_instances(self):
        mock_return = map(create_mock_attrs, [{"id":1},{"id":2}])
        mock_client = mock.Mock()
        mock_client.api_get.return_value = mock_return
        self.resource.client = mock_client
        result = self.resource.get_test_sub_resources()
        for res in result:
            self.assertIsInstance(res, TestSubResource)
        self.assertEqual(set([1,2]), set([item.id for item in result]))

    def test_resource_is_correct_instance(self):
        """
        Expose an issue where the closure which creates sub_resource functions
        in the `Resource` constructor does not close over the class name
        correctly and thus every sub_resource function ends up referencing
        the same class.
        """
        mock_client = mock.Mock()
        mock_client.api_get.return_value = [create_mock_attrs({"id":"1"})]
        self.resource.client = mock_client
        result = self.resource.get_test_sub_resources()
        self.assertIsInstance(result[0], TestSubResource)
        

class FindResourceTestCase(unittest.TestCase):

    def test_find_resource_by_id_with_client(self):
        client = mock.Mock()
        client.api_get.return_value = {"id":"1"}
        resource = TestResource.find_with_client("1", client)
        self.assertEqual(resource.id, "1")

    def test_find_resource_without_details_throws_clienterror(self):
        self.assertRaises(gocardless.exceptions.ClientError, TestResource.find, 1)

    @patch('gocardless.client')
    def test_find_resource_without_client(self, mock_client):
        mock_client.api_get.return_value = {"id":"1"}
        self.assertEqual(TestResource.find("1").id, "1")




