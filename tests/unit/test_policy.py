import json
import unittest

from policy_maker import app

class TestPolicy(unittest.TestCase):

  def setUp(self):
    self.bucket_name = 'some-bucket-name'
    self.principals = ["arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"]
    self.maxDiff = None

  def test_policy_output(self):
    policy = app.create_policy_document(
      "999999999999",
      bucket_name=self.bucket_name,
      principals=self.principals)
    result = json.loads(policy)
    exptected = {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "SynapseObjectAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": [
              "arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"
            ]
          },
          "Action": [
            "s3:*Object*",
            "s3:*MultipartUpload*"
          ],
          "Condition": {
            "StringEquals": {
              "aws:PrincipalAccount": "325565585839"
            }
          },
          "Resource": "arn:aws:s3:::some-bucket-name/*"
        },
        {
          "Sid": "BucketAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": [
              "arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"
            ]
          },
          "Action": [
            "s3:ListBucket*",
            "s3:GetBucketLocation"
          ],
          "Resource": "arn:aws:s3:::some-bucket-name"
        },
        {
          "Sid": "ReadObjectAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": [
              "arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"
            ]
          },
          "Action": [
            "s3:GetObject",
            "s3:GetObjectAcl",
            "s3:AbortMultipartUpload",
            "s3:ListMultipartUploadParts"
          ],
          "Resource": "arn:aws:s3:::some-bucket-name/*"
        },
        {
          "Sid": "InternalPutObjectAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": [
              "arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"
            ]
          },
          "Action": [
            "s3:PutObject",
            "s3:PutObjectAcl"
          ],
          "Condition": {
            "StringEquals": {
              "aws:PrincipalAccount": "999999999999"
            }
          },
          "Resource": "arn:aws:s3:::some-bucket-name/*"
        },
        {
          "Sid": "ExternalPutObjectAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": [
              "arn:aws:iam::1111111111111:user/joe.smith@sagebase.org"
            ]
          },
          "Action": [
            "s3:PutObject",
            "s3:PutObjectAcl"
          ],
          "Condition": {
            "StringEquals": {
              "s3:x-amz-acl": "bucket-owner-full-control"
            }
          },
          "Resource": "arn:aws:s3:::some-bucket-name/*"
        }
      ]
    }
    self.assertDictEqual(exptected, result)
