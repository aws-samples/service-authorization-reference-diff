import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import { ScheduledFunction } from './scheduled-function';
import {EmailSubscription} from 'aws-cdk-lib/aws-sns-subscriptions';

export class SarDiffGeneratorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const authHistoryBucket = new s3.Bucket(this, 'AuthHistoryBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [
        {
          expiration: cdk.Duration.days(30)
        }
      ]
    });

    const notificationTopic = new sns.Topic(this, 'ChangeNotificationTopic');

    // Add new subscriptions here.  These can be email subscribers or programmatic subscribers.
    // notificationTopic.addSubscription(new EmailSubscription('<youremail>@example.com'));

    // Example of an SQS subscriber
    // notificationTopic.addSubscription(new SqsSubscription(myQueue));

    new ScheduledFunction(this, 'ScheduledFunction', {
      authHistoryBucket: authHistoryBucket,
      notificationTopic: notificationTopic
    });
  }
}
