import boto3
import json

import chunker
import os
import requests

from constants import auth_reference_history_bucket
from diffs import DiffEvaluator, DiffReport

base_sar_url = 'https://servicereference.us-east-1.amazonaws.com/'

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')


def handler(event, context):
	r = requests.get(base_sar_url)
	r.raise_for_status()
	service_auth_reference_manifest = r.json()

	service_differences = []
	for service_auth_reference_url in service_auth_reference_manifest:
		service_difference = DiffEvaluator(service_auth_reference_url)
		diff = service_difference.calculate_diff()
		if diff is not None:
			service_differences.append(diff)

	diff_report = DiffReport(service_differences)
	if not diff_report.has_differences():
		print('No differences detected.')
		return

	output = diff_report.to_json()

	output_as_string = json.dumps(output)
	output_chunks = chunker.chunk_output(output_as_string)

	for chunk in output_chunks:
		sns_client.publish(
			TopicArn=os.environ['AUTH_REFERENCE_CHANGE_TOPIC_ARN'],
			Message=chunk
		)

	# copy new auth files to old file bucket, but only those that have changed
	for service_diff in diff_report.service_differences:
		print(f'Copying {service_diff.service_auth_reference_path} to history bucket')
		s3_client.put_object(
			Bucket=auth_reference_history_bucket,
			Body=bytes(json.dumps(service_diff.new_auth_reference).encode('UTF-8')),
			Key=service_diff.service_auth_reference_path
		)


if __name__ == "__main__":
	handler({}, {})
