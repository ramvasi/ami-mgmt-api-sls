@ABGN-9765-ec2-ami-delete-api
@integration_test

Feature: Delete exception AMIs from AppSync Acccount table

  Scenario Outline: Positive Scenario 1 - Remove exempted AMI from AppSync Acccount table
    Given DELETE API /v1/accounts/<account_id>/regions/<region>/amis/<image>/vpcs/<vpc>/ami_exception exists
      And valid oauth2 token for API authorization generated
      And VPCx account <account_id> is valid
      And Exception for the <image> exists in the accounts table - <exists>
    When we invoke the API to remove <image>, <region>, <vpc> from <account_id>
    Then API returns a status of 200 
      And the AMI exception is removed from AppSync Acccount table
    Examples: 
      | image     | region     | vpc    | account_id | exists |
      | bdd_image | bdd_region | vpc_id | bdd_acc    | yes    | 
      | BAD_image | bdd_region | vpc_id | bdd_acc    | no     |

  Scenario Outline: Negative Scenario 1 - Remove exempted AMI from non existant AppSync Acccount table
    Given DELETE API /v1/accounts/<account_id>/regions/<region>/amis/<image>/vpcs/<vpc>/ami_exception exists
      And valid oauth2 token for API authorization generated
      And VPCx account <account_id> does not exist
    When we invoke the API to remove <image>, <region>, <vpc> from <account_id>
    Then API returns a status of 404 
    Examples:
      | image     | region     | vpc    | account_id  |
      | bdd_image | bdd_region | vpc_id | invalid_acc |
