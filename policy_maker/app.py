import json
import logging
import traceback

import boto3
from botocore.exceptions import ClientError
from crhelper import CfnResource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

SYNAPSE_AWS_ACCOUNT_ID = "325565585839"

def get_client(service):
  return boto3.client(service)


def get_params(event):
  '''Find the params specified for the custom resource'''
  parameters = event['ResourceProperties']

  bucket_name = parameters.get('BucketName', None)
  if bucket_name is None:
    raise Exception('Required parameters: BucketName')

  extra_principals = parameters.get('ExtraPrincipalArns', None)
  if not extra_principals:
    extra_principals = []
  elif not isinstance(extra_principals, list):
    extra_principals = [extra_principals]
  # strip empties
  extra_principals = [extra for extra in extra_principals if extra]

  log.debug((f'Params returned from get_params: bucket_name={bucket_name}, '
    f'extra_principals={extra_principals}'))
  return bucket_name, extra_principals


def get_bucket_tags(bucket):
  '''Retrieve tags for an s3 bucket'''
  s3 = get_client('s3')
  try:
    response = s3.get_bucket_tagging(Bucket=bucket)
  except ClientError as e:
    log.debug(e.response['Error']['Message'])
    raise e
  log.debug(f'S3 bucket tags response: {response}')
  tags = response.get('TagSet')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')
  return tags


def get_principal_tag(tags):
  '''Find the value of the principal tag'''
  principal_tag_name = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_tag_name:
      tag_value = tag.get('Value')
      return tag_value
  else:
    raise ValueError(f'Could not derive a value for {principal_tag_name} from tags')


def combine_principals(principal, extra_principals):
  principals = [principal]
  if extra_principals is not None:
    principals = extra_principals + principals
  return principals


def create_policy_document(aws_account_id, bucket_name, principals):
  bucket_arn = f'arn:aws:s3:::{bucket_name}'
  bucket_objects_arn = f'{bucket_arn}/*'
  policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyInsecureAccess",
            "Effect": "Deny",
            "Principal": '*',
            "Action": "s3:*",
            "Resource": [
                bucket_arn,
                bucket_objects_arn,
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false",
                },
            },
        },
        {
            "Sid": "SynapseObjectAccess",
            "Effect": "Allow",
            "Principal": {
              'AWS': principals
            },
            "Action": [
                "s3:*Object*",
                "s3:*MultipartUpload*"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalAccount": SYNAPSE_AWS_ACCOUNT_ID
                }
            },
            "Resource": bucket_objects_arn
        },
        {
            "Sid": "BucketAccess",
            "Effect": "Allow",
            "Principal": {
              'AWS': principals
            },
            "Action": [
                "s3:ListBucket*",
                "s3:GetBucketLocation"
            ],
            "Resource": bucket_arn
        },
        {
            "Sid": "ReadObjectAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": principals
            },
            "Action": [
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": bucket_objects_arn
        },
        {
            "Sid": "PutObjectAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": principals
            },
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject*",
                "s3:*MultipartUpload*"
            ],
            "Resource": bucket_objects_arn
        }
    ]
  }

  return json.dumps(policy)


def attach_policy(bucket_name, policy_document):
  '''Add a policy to the bucket'''
  s3 = get_client('s3')
  try:
    s3.put_bucket_policy(Bucket=bucket_name, Policy=policy_document)
  except ClientError as e:
    log.debug(e.response['Error']['Message'])
    raise e


@helper.update
@helper.create
def create(event, context):
  '''Create or re-create the policy'''
  bucket_name, extra_principals = get_params(event)
  tags = get_bucket_tags(bucket_name)
  principal_arn = get_principal_tag(tags)
  principals = combine_principals(
    principal=principal_arn,
    extra_principals=extra_principals)
  aws_account_id = get_client('sts').get_caller_identity().get('Account')
  policy_document = create_policy_document(
    aws_account_id,
    bucket_name=bucket_name,
    principals=principals)
  attach_policy(bucket_name, policy_document)
  aws_request_id = context.aws_request_id
  physical_resource_id = f'BucketPolicy_{bucket_name}_{aws_request_id}'
  if event['RequestType'] == 'Update':
    return event['PhysicalResourceId']
  else:
    return physical_resource_id


@helper.delete
def delete(event, context):
  '''Delete the policy'''
  bucket_name, _ = get_params(event)
  s3 = get_client('s3')
  try:
    s3.delete_bucket_policy(Bucket=bucket_name)
  except ClientError as e:
    log.debug(e.response['Error']['Message'])
    # do not raise if the bucket has already been removed
    if e.response['Error']['Code'] != 'NoSuchBucket':
      raise e
  return event['PhysicalResourceId']


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
