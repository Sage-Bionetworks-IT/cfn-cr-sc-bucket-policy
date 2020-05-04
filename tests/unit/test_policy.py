import json
import unittest

from policy_maker import app

class TestPolicy(unittest.TestCase):

  def setUp(self):
    self.bucket_name = 'some-bucket-name'
    self.principals = []
    self.maxDiff = None

  def test_policy_output(self):
    result = app.create_policy_document(
      bucket_name=self.bucket_name,
      principals=self.principals)
    expected = '{"Version": "2012-10-17", "Statement": [{"Sid": "ReadAccess", "Effect": "Allow", "Principal": {"AWS": []}, "Action": ["s3:ListBucket*", "s3:GetBucketLocation"], "Resource": "arn:aws:s3:::some-bucket-name"}, {"Sid": "WriteAccess", "Effect": "Allow", "Principal": {"AWS": []}, "Action": ["s3:*Object*", "s3:*MultipartUpload*"], "Resource": "arn:aws:s3:::some-bucket-name/*"}]}'
    self.assertEqual(result, expected)
