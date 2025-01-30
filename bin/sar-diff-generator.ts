#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SarDiffGeneratorStack } from '../lib/sar-diff-generator-stack';

const app = new cdk.App();
new SarDiffGeneratorStack(app, 'SarDiffGeneratorStack', {});