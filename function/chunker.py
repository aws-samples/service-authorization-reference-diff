import json


sns_max_message_size_bytes = 262144


def chunk_output(output_as_string):
	output_as_string = [output_as_string]

	chunked_output = []
	for output in output_as_string:
		if len(output.encode('utf-8')) >= sns_max_message_size_bytes:
			output1, output2 = _chunk(output)
			chunked_output.extend(chunk_output(output1))
			chunked_output.extend(chunk_output(output2))
		else:
			chunked_output.append(output)

	return chunked_output


def _chunk(output_as_string):
	output_as_json = json.loads(output_as_string)

	new_actions = output_as_json['NEW_ACTIONS']
	removed_actions = output_as_json['REMOVED_ACTIONS']

	new_actions1, new_actions2 = _split_array(new_actions)
	removed_actions1, removed_actions2 = _split_array(removed_actions)

	output1 = {
		'NEW_ACTIONS': new_actions1,
		'REMOVED_ACTIONS': removed_actions1
	}

	output2 = {
		'NEW_ACTIONS': new_actions2,
		'REMOVED_ACTIONS': removed_actions2
	}

	return json.dumps(output1), json.dumps(output2)


def _split_array(array):
	midpoint = len(array) // 2
	return array[:midpoint], array[midpoint:]
