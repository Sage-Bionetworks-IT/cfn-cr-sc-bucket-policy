import unittest
from unittest.mock import MagicMock

import boto3
import botocore
from botocore.stub import Stubber

from policy_maker import app


class TestAttachPolicy(unittest.TestCase):

  def test_happy_path(self):
    s3 = boto3.client('s3')
    response = {
      'ResponseMetadata': {
        'RequestId': 'A73C8CFD9C5CCEA2',
        'HostId': 'b737XWjh8TbHHcq+Ttnf1yJeEMjdAJ8kNh9VOl0ReiOIaGEG3hiI7e7bP8P',
        'HTTPStatusCode': 204,
        'HTTPHeaders': {},
        'RetryAttempts': 0
      }
    }
    with Stubber(s3) as stubber:
      bucket_name = 'some-bucket-name'
      policy_document = '{}'
      expected_params = {
        'Bucket': bucket_name,
        'Policy': policy_document
      }
      stubber.add_response(
        method='put_bucket_policy',
        service_response=response,
        expected_params=expected_params)
      app.get_client = MagicMock(return_value=s3)
      app.attach_policy(bucket_name, policy_document)

  def test_error_raised(self):
    s3 = boto3.client('s3')

    with Stubber(s3) as stubber, \
      self.assertRaises(botocore.exceptions.ClientError):
      stubber.add_client_error(
        method='put_bucket_policy',
        service_error_code='MalformedPolicy',
        service_message="Policies must be valid JSON and the first byte must be '{'",
        http_status_code=400)
      bucket_name = 'some-bucket-name'
      policy_document = ''
      app.get_client = MagicMock(return_value=s3)
      app.attach_policy(bucket_name, policy_document)
