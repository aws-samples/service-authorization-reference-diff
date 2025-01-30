## Service authorization reference diff generator

Deploys a Lambda function and supporting infrastructure to your account that runs on a schedule (daily, by default) and notifies you of any new IAM actions or services that were released since the previous run.

Publishes a message to an SNS topic with the JSON format:

```json
{
  "NEW_ACTIONS": ["service:action1", "service:action2"],
  "REMOVED_ACTIONS": ["service:action1", "service:action2"]
}
```

### Getting Started

Prerequisities:

- [Install and configure the AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install)
- Install [make](https://www.gnu.org/software/make/manual/make.html)

Deployment:

1. Edit the file lib/sar-diff-generator-stack.ts and follow the example to add subscribers for the notifications.

2. Run the following command to deploy the infrastructure
   ```
   make deploy
   ```

Infrastructure deployed:

- Lambda function that runs the diff generator code
  - IAM role attached to the Lambda function
- S3 bucket that stores previous copies of the service authorization reference
- SNS topic that notifies subscribers of changes
- EventBridge rule that runs daily

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

