import unittest

from policy_maker import app


class TestGetParams(unittest.TestCase):

  def test_bucketname_present(self):
    bucket_name = 'some-bucket'
    event = {
      'ResourceProperties': {
        'BucketName': bucket_name
      }
    }
    result = app.get_params(event)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0], bucket_name)
    self.assertEqual(result[1], [])


  def test_bucketname_missing(self):
    with self.assertRaises(Exception):
      event = { 'ResourceProperties': {} }
      result = app.get_params(event)


  def test_principals_present(self):
    principals = ['foo', 'bar']
    event = {
      'ResourceProperties': {
        'BucketName': 'some-bucket',
        'ExtraPrincipalArns': principals
      }
    }
    result = app.get_params(event)
    self.assertCountEqual(principals, result[1])


  def test_string_principals_converted_to_list(self):
    principals = 'foobar'
    event = {
      'ResourceProperties': {
        'BucketName': 'some-bucket',
        'ExtraPrincipalArns': principals
      }
    }
    result = app.get_params(event)
    self.assertCountEqual([principals], result[1])
