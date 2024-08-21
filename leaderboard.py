import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Leaderboard')


def get_leaderboard(limit=10):
	"""
	Get the leaderboard and return the top n participants
	:param limit:
	:return: list of participants
	"""
	response = table.scan()
	items = sorted(response['Items'], key=lambda x: x['points'], reverse=True)
	return items[:limit]


def get_participant_points(user_id):
	"""
	Get the points for a participant
	:param user_id:
	:return: points
	"""
	response = table.get_item(
		Key={
			'userID': user_id
		}
	)
	return response.get('Item')


def add_or_update_points(user_id, event_points):
	"""
	Adds points for a participant, adds participant if doesnt exist
	:param user_id:
	:param event_points:
	:return:
	"""
	response = table.get_item(Key={'userID': user_id})

	if 'Item' in response:
		total_points = response['Item']['points'] + event_points
	else:
		total_points = event_points

	# update the leaderboard
	response = table.put_item(
		Item={
			'userID': user_id,
			'points': total_points
		}
	)
	return response


def delete_participant(user_id):
	"""
	Delete a participant from the leaderboard
	:param user_id:
	:return:
	"""
	response = table.delete_item(
		Key={
			'userID': user_id
		}
	)
	return response
