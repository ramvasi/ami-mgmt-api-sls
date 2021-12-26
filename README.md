# Centralized AMI Management API
AMI management API puts/deletes an AMI id to list of approved AMIs. The exception will be stored in AppSync service account metadata table in DynamoDB.

### Sample schema for the AppSync account metadata table is below:

| id | __typename | ami_exceptions | aws_number  | createdAt | db_service_accounts | db_users | dbas | exceptions_regex | external_users | log_buckets | new_api_users | owner  | pb_exceptions | project_id |regions| s3_bucket_policy_admin | s3_bucket_policy_exception_buckets    | s3x_bucket_roles | s3x_ip_list | services  | updatedAt  | vpc_list                                                                                                                                   |
|--------------------------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|--------------------------|---------------------|----------|------|------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|---------------|------------|---------------------------------------|------------------------|----------------------------------------------------|------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| 355ac74dfa10bc6b8 | Account    | [] | 63121 | 2020-11-16T18:58:59.704Z |                     |          |      |                  | []             | {"all": "itx--logsallregions-z6wkusdugxb5", "catchall": "itx--logsall-2rshxi63e", "eu-west-1": "itx--logseuwe1-ms4ufvvpo", "ap-southeast-1": "itx--logsapse1-1w3txg6vb2", "ap-northeast-1": "itx--logsapne1-1skqpnzkr"} | []            | joe |               | itx-04    | [{"S":"us-east-1"},{"S":"eu-west-1"}] | false                  | [{"S":"carlos-source"},{"S":"carlos-destination"}] | []               | []          | [{"S":"Batchx"},{"S":"Lambdax"},{"S":"KMSx"},{"S":"Kinesisx"},{"S":"RDSx"},{"S":"CloudFrontx"},{"S":"EMRx"},{"S":"Athenax"},{"S":"EC2x"},{"S":"ElasticTranscoderx"},{"S":"AppStreamx"},{"S":"Gluex"},{"S":"Cognitox"}] | 2021-10-22T21:08:37.927Z | [{"S":"vpc-a8cqwsd\us-east-1\10.37.230.128/27,10.34.158.96/27\none"}] |

In a multi-account AWS Org implementation,  application teams some times need to use custom AMIs or non-golden AMIs. 
By default they are only allowed to use only golden AMIs, but on exception use-cases they can use a custom AMI.
Exception AMIs are owned by external vendors in most cases and shared with the account that needs to use it.
This API will be used to track the exception AMIs at the account level, and allow users to create EC2 instances from them.

### AMI Exception String Format:
````shell script
"<image_id>_<region_name>_<vpc_id>"
````
Each account record in the account metadata table will have a list of AMI Exception strings.
Example Exceptions:
    
|AMI| 	Region| 	Account| 	VPC |	comment |
|-----|-----|-----|-----|-----|
|AMI 2 |	us-east-2 |	itx-000 |	* |	exception ami for an account |
|AMI 3 |	us-east-2 |	itx-016 |	vpc-1234 |	exception ami for an account and vpc |
|* |	us-west-1 |	itx-046 |	vpc-789 |	exception vpc - allowed to host any AMI |

### Consumers of the API: 
Exception process that adds special AMI to a particular account or VPC.

### Pre-reqs:
AMI Image(s) must be shared with end-user account before calling AMI exception API

### Features of the API: 

    List of AMI exceptions will be stored in AppSync service account table in dynamo DB
    Put request is idempotent
    Put will be used to create and/or update an AMI exception entry in AppSync account table
    An Asterix[*] will be used as wildcard character
    Valid parameter definitions:
        Region passed should be valid region in the list of regions for that account. 
        A valid AMI <image-id> is an AMI that is available for provisioning in end-user AWS Account in the associated region
        A valid region <region-name> is the AWS region in which AMI is located. If AMI is a wildcard, then the region may be any AWS region listed in AppSync Account table for that account (i.e. region that is allowed in test-org)
        A valid account <account-id> is a test-org secondary AWS account provisioned and monitored by xBot Central account
        A valid VPC <vpc-id> is a VPC that exists in a valid test-org VPCx secondary AWS account
    Put request parameter rules for Exempt AMI:
        <region_name> must be valid and cannot be wildcard.
        <account_name> must be valid and cannot be wildcard.
        <image-id> or <vpc-id> may be wildcard under certain conditions, but not both.
    If exception exists for  image+region+account+VPC1 and another request comes for VPC2 - then we will add a new entry for  image+region+account+VPC2 without changing the previous entry
    AMI scope increase process [Fine-grained to wildcard]:
        If the account has exception for specific AMI and specific VPC and now requesting exception for same AMI for all VPCs
        For VPC, delete all VPC records for the given image+region+account and insert new record with image+region+account+wildcard
    AMI scope downgrade process [Wildcard to fine-grained]:
        If the account has exception for specific AMI for all VPC and now requesting exception for same AMI for specific VPC
        API will update wildcard with specific valid vpc-id for the AMI
    


## Architecture
![Architecture2](docs/arch.png)

```
.
├── README.md                     <-- This documentation file
├── config                        <-- Configurations for each environment
├── docs                          <-- API documentations
├── sls
│   ├── ami_excetion              <-- Source code for Lambda functions
│   └── utils                     <-- Functions shared by multiple Lambdas
├── scripts                       <-- Deployment scripts
├── Pipfile                       <-- Python dependencies
├── package.json                  <-- Serverless frameowrk dependencies
└── serverless.yml                <-- Serverless application definition file
```

## Example Usage

```bash
# adds/updates ami exception in appsync account table
curl -X PUT 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
     -H 'Host: <api-instance>.execute-api.us-east-1.amazonaws.com' 
     http://vpcx.apigw.amazonaws.com/dev/v1/accounts/itx-046/regions/us-east-2/amis/ami-0443305dabd4be2bc/vpcs/*/ami_exception

# deletes ami exception in appsync account table
curl -X DELETE 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
     -H 'Host: <api-instance>.execute-api.us-east-1.amazonaws.com' 
     http://vpcx.apigw.amazonaws.com/dev/v1/accounts/itx-046/regions/us-east-2/amis/ami-0443305dabd4be2bc/vpcs/*/ami_exception

```

## External dependencies

This application uses AppSync service account metadata table.


## Local env setup

```
# Installs both main and dev dependencies
pipenv install --dev
```

## Test

```
# Unit test 
pytest ./

```

## Deployment

```
serverless deploy -s dev
```

## BDD Integration Tests

```
behave sls/ami_exception/tests/bdd
```

## OpenAPI Spec
The OpenAPI spec for the API is located at [docs/openapi.yaml](docs/openapi.yaml)