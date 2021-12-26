@ABGN-7695-ec2-ami-mgmt-put-api
@integration_test

Feature: Add exception AMIs to AppSync Acccount table

  Scenario Outline: Positive Scenario 1 - Add a valid Exempted AMI to AppSync Acccount table
    Given PUT API /v1/accounts/<account_id>/regions/<region_name>/amis/<image_id>/vpcs/<vpc>/ami_exception exists
      And valid oauth2 token for API authorization generated
      And AMI <image_id> is valid
      And Region <region_name> is valid
      And VPCx account <account_id> is valid
      And VPC <vpc> is valid
    When we invoke the API to add <image_id>, <region_name>, <account_id>, <vpc>
    Then API returns a status of 200 
      And the AMI image is added to the AppSync Acccount table for <vpc>
    Examples: 
      |   ami-exception-entry             |  vpc   |   account  |
      | <image_id>_<region_name>_<vpc_id> | vpc_id | account_id |

  Scenario Outline: Positive Scenario 2 - Upgrade an Exempted AMI VPC scope from fine-grained to wildcard
    Given PUT API /v1/accounts/<account_id>/regions/<region_name>/amis/<image_id>/vpcs/<vpc>/ami_exception exists
      And valid oauth2 token for API authorization generated
      And AMI <image_id> is valid
      And Region <region_name> is valid
      And VPCx account <account_id> is valid
      And VPC <vpc> is valid
      And AMI exception entry exists for <image_id> + <region_name> + <account_id> + specific vpc
    When we invoke the API to add <image_id>, <region_name>, <account_id>, <vpc>
    Then API returns a status of 200
      And the AMI image is added to the AppSync Acccount table for <vpc>
      And previous entry(s) AppSync Acccount table for the AMI with fine-grained VPC id are <old_record_state>
    Examples:   
      |       ami-exception-entry          |   vpc   |   account  | old_record_state |
      | <image_id>_<region_name>_*         |    *    |    *       |    deleted       |

  Scenario Outline: Positive Scenario 3 - Downgrade an Exempted AMI VPC scope from wildcard to fine-grained
    Given PUT API /v1/accounts/<account_id>/regions/<region_name>/amis/<image_id>/vpcs/<vpc>/ami_exception exists
      And valid oauth2 token for API authorization generated
      And AMI <image_id> is valid
      And Region <region_name> is valid
      And VPCx account <account_id> is valid
      And VPC <vpc> is valid
      And AMI exception entry exists for <image_id> + <region_name> + <account_id> + wild card vpc
    When we invoke the API to add <image_id>, <region_name>, <account_id>, <vpc>
    Then API returns a status of 200 
      And existing entry in AppSync Acccount table for the AMI's VPC is updated from wildcard to <vpc>
    Examples: 
      |   ami-exception-entry             |  vpc   |   account  |
      | <image_id>_<region_name>_<vpc_id> | vpc_id | account_id |
