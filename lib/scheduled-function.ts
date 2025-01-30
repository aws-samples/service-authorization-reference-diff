import { Construct } from 'constructs';

import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cdk from 'aws-cdk-lib';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { ManagedPolicy, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';

interface ScheduledFunctionProps {
    authHistoryBucket: s3.Bucket;
    notificationTopic: sns.Topic;
}

export class ScheduledFunction extends Construct {
  constructor(scope: Construct, id: string, {
        authHistoryBucket,
        notificationTopic
    }: ScheduledFunctionProps) {
    super(scope, id);

    const functionRole = new Role(this, 'ApiFunctionRole', {
      assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
    });
    functionRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));

    const lambdaFunction = new lambda.Function(this, 'Function', {
        runtime: lambda.Runtime.PYTHON_3_10,
        code: lambda.Code.fromAsset('function/function.zip'),
        handler: 'handler.handler',
        timeout: cdk.Duration.minutes(10),
        logRetention: RetentionDays.TWO_WEEKS,
        role: functionRole,
        memorySize: 512
    });

    authHistoryBucket.grantReadWrite(lambdaFunction);
    lambdaFunction.addEnvironment('AUTH_REFERENCE_HISTORY_BUCKET', authHistoryBucket.bucketName);

    notificationTopic.grantPublish(lambdaFunction);
    lambdaFunction.addEnvironment('AUTH_REFERENCE_CHANGE_TOPIC_ARN', notificationTopic.topicArn);
  
    new events.Rule(this, 'RunDailyRule', {
        description: "Runs daily",
        schedule: events.Schedule.cron({
            month: "*",
            weekDay: "*",
            hour: "21",
            minute: "0",
        }),
        targets: [new targets.LambdaFunction(lambdaFunction)],
        enabled: true
    });
  }
}

