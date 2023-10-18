# cfn-cr-sc-bucket-policy

Cloudformation Custom Resource that creates a S3 BucketPolicy. This is intended
only for use in ServiceCatalog, as it retrieves an ARN that Service Catalog sets,
`aws:servicecatalog:provisioningPrincipalArn`, to set as a principal on the
BucketPolicy.

Inventory of source code and supporting files:

- policy_maker - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

## Use in a Cloudformation Template
Create a custom resource in your cloud formation template. Here's an example:
```yaml
  S3Bucket:
    Type: AWS::S3::Bucket

  SCS3BucketPolicy:
    Type: Custom::SCS3BucketPolicy
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-sc-bucket-policy-FunctionArn'
      BucketName: !Ref S3Bucket
      ExtraPrincipalArns: !Ref S3UserARNs
```

The creation of the custom resource triggers the lambda. It creates an S3
BucketPolicy.
* `ServiceToken` refers to the ARN of the lambda function. You can follow the pattern given; see "Install Lambda into AWS" below for the stack that exports that value.
* The only required property is `BucketName`, a String.
* `ExtraPrincipalArns` is one or more valid IAM policy [principals](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html).

## Development

### Contributions
Contributions are welcome.

### Setup Development Environment

Install the following applications:
* [AWS CLI](https://github.com/aws/aws-cli)
* [AWS SAM CLI](https://github.com/aws/aws-sam-cli)
* [pre-commit](https://github.com/pre-commit/pre-commit)
* [pipenv](https://github.com/pypa/pipenv)

### Install Requirements

Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Update Requirements

First, make any needed updates to the base requirements in `Pipfile`, then use
`pipenv` to regenerate both `Pipfile.lock` and `requirements.txt`.

```shell script
$ pipenv update --dev
```

We use `pipenv` to control versions in testing, but `sam` relies on
`requirements.txt` directly for building the lambda artifact, so we dynamically
generate `requirements.txt` from `Pipfile.lock` before building the artifact.
The file must be created in the `CodeUri` directory specified in
`template.yaml`.

```shell script
$ pipenv requirements > requirements.txt
```

Additionally, `pre-commit` manages its own requirements.

```shell script
$ pre-commit autoupdate
```

### Create a local build

Use a Lambda-like docker container to build the Lambda artifact

```shell script
$ sam build --use-container
```

### Run unit tests

Tests are defined in the `tests` folder in this project, and dependencies are
managed with `pipenv`. Install the development dependencies and run the tests
using `coverage`.

```shell script
$ pipenv run coverage run -m pytest tests/ -svv
```

Automated testing will upload coverage results to [Coveralls](coveralls.io).

### Run integration tests

Running integration tests
[requires docker](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html)

```shell script
$ sam local invoke Function --event events/event.json
```

## Deployment

### Build

```shell script
sam build
```

## Deploy Lambda to S3
This requires the correct permissions to upload to bucket
`bootstrap-awss3cloudformationbucket-19qromfd235z9`.

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/cfn-cf-sc-bucket-policy.yaml

aws s3 cp .aws-sam/build/cfn-cf-sc-bucket-policy.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cf-sc-bucket-policy/master
```

## Install Lambda into AWS
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/cfn-cf-sc-bucket-policy.yaml
```yaml
template_path: "remote/cfn-cf-sc-bucket-policy.yaml"
stack_name: "cfn-cf-sc-bucket-policy"
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
hooks:
  before_launch:
    - !cmd "curl https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cf-sc-bucket-policy/master/cfn-cf-sc-bucket-policy.yaml --create-dirs -o templates/remote/cfn-cf-sc-bucket-policy.yaml"
```

Install the lambda using sceptre:
```bash script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-cf-sc-bucket-policy
```
