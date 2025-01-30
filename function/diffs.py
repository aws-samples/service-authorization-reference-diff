from typing import Optional

import boto3
import json
import requests

from urllib.parse import urlparse
from constants import auth_reference_history_bucket
from botocore.exceptions import ClientError


class DiffEvaluator:
	def __init__(self, service_auth_reference_metadata):
		self.service_auth_reference_url = service_auth_reference_metadata['url']
		self.service_name = service_auth_reference_metadata['service']
		self.s3_client = boto3.client('s3')
		parse_result = urlparse(self.service_auth_reference_url)
		self.service_auth_reference_path = parse_result.path.lstrip("/")

	def _get_auth_reference(self, bucket_name):
		auth_reference = self.s3_client.get_object(
			Bucket=bucket_name,
			Key=self.service_auth_reference_path
		)
		return json.loads(auth_reference['Body'].read())

	def get_old_auth_reference(self):
		try:
			return self._get_auth_reference(auth_reference_history_bucket)
		except ClientError as e:
			if e.response['Error']['Code'] == 'NoSuchKey':
				return None
			else:
				raise

	def get_new_auth_reference(self):
		print(f'Downloading from {self.service_auth_reference_url}..')
		r = requests.get(self.service_auth_reference_url)
		r.raise_for_status()
		return r.json()

	def calculate_diff(self) -> Optional['ServiceDifference']:
		"""
		Returns a string output listing the differences between the old and new SAR.  Returns None if there are no
		differences.
		"""
		new_auth_reference = self.get_new_auth_reference()
		service_prefix = new_auth_reference['Name']

		service_difference = ServiceDifference(service_prefix, new_auth_reference, self.service_auth_reference_path)
		old_auth_reference = self.get_old_auth_reference()
		if old_auth_reference is None:
			for action in new_auth_reference.get('Actions', []):
				service_difference.add_new_action(action)
			return service_difference

		new_auth_reference_actions = new_auth_reference['Actions']
		old_auth_reference_actions = old_auth_reference['Actions']

		# both old and new exist, calculate diffs
		old_action_names = [old_action['Name'] for old_action in old_auth_reference_actions]
		new_action_names = [new_action['Name'] for new_action in new_auth_reference_actions]

		action_names_that_were_added = set(new_action_names) - set(old_action_names)
		action_names_that_were_removed = set(old_action_names) - set(new_action_names)

		if len(action_names_that_were_added) > 0:
			actions_to_add = [action for action in new_auth_reference_actions if action['Name'] in action_names_that_were_added]
			for action in actions_to_add:
				service_difference.add_new_action(action)

		if len(action_names_that_were_removed) > 0:
			actions_to_remove = [action for action in old_auth_reference_actions if action['Name'] in action_names_that_were_removed]
			for action in actions_to_remove:
				service_difference.add_removed_action(action)

		if service_difference.has_differences():
			return service_difference

		return None


class ServiceDifference:
	def __init__(self, service_name, new_auth_reference, service_auth_reference_path):
		self.service_name = service_name
		self.new_auth_reference = new_auth_reference
		self.service_auth_reference_path = service_auth_reference_path
		self.removed_actions = []
		self.new_actions = []

	def add_new_action(self, action):
		# save the entire complex action object for now to make this easier to evolve as more fields are added
		self.new_actions.append(action)

	def add_removed_action(self, action):
		self.removed_actions.append(action)

	def has_differences(self):
		return len(self.removed_actions) > 0 or len(self.new_actions) > 0

	def combine_with(self, other_service_diff: 'ServiceDifference'):
		self.new_actions.extend(other_service_diff.new_actions)
		self.removed_actions.extend(other_service_diff.removed_actions)

	def to_string(self):
		output = [f'\t{self.service_name}\n']

		for diff in self.action_differences:
			output.append(f'\t\t{diff.to_string()}')

		return ''.join(output)


class DiffReport:
	def __init__(self, service_differences: [ServiceDifference]):
		self.service_differences: [ServiceDifference] = service_differences

	def has_differences(self):
		return len(self.service_differences) > 0

	def to_json(self):
		new_actions = []
		removed_actions = []

		for diff in self.service_differences:
			for action in diff.new_actions:
				print(f'Detected new action {action["Name"]} for service {diff.service_name}')
				new_actions.append(f'{diff.service_name}:{action["Name"]}')

			for action in diff.removed_actions:
				print(f'Detected removed action {action["Name"]} for service {diff.service_name}')
				removed_actions.append(f'{diff.service_name}:{action["Name"]}')

		return {
			'NEW_ACTIONS': new_actions,
			'REMOVED_ACTIONS': removed_actions
		}
