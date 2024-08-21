import json
import boto3

# Use DynamoDB
# dynamodb = boto3.resource('dynamodb')

# Use the local DynamoDB instance
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
table = dynamodb.Table('Leaderboard')


def lambda_handler(event, context):
	"""
	Entry point for the Lambda function to handle different API requests
	"""
	try:
		http_method = event['httpMethod']
		path = event['path']

		if http_method == 'POST' and path == '/points':
			body = json.loads(event['body'])
			user_id = body['userID']
			event_points = body['points']
			return add_or_update_points(user_id, event_points)

		elif http_method == 'GET' and path == '/leaderboard':
			limit = int(event['queryStringParameters'].get('limit', 10))
			return get_leaderboard(limit)

		elif http_method == 'GET' and path.startswith('/participant/'):
			user_id = event['pathParameters']['userID']
			return get_participant_points(user_id)

		elif http_method == 'DELETE' and path.startswith('/participant/'):
			user_id = event['pathParameters']['userID']
			return delete_participant(user_id)

		else:
			return {
				'statusCode': 400,
				'body': json.dumps({'message': 'Invalid request'})
			}
	except Exception as e:
		return {
			'statusCode': 500,
			'body': json.dumps({'message': str(e)})
		}


def get_leaderboard(limit=10):
	"""
	Get the leaderboard and return the top n participants
	:param limit: Number of top participants to return
	:return: List of participants sorted by points
	"""
	response = table.scan()
	items = sorted(response['Items'], key=lambda x: x['points'], reverse=True)
	return {
		'statusCode': 200,
		'body': json.dumps(items[:limit])
	}


def get_participant_points(user_id):
	"""
	Get the points for a participant
	:param user_id: The ID of the participant
	:return: The participant's points and details
	"""
	response = table.get_item(
		Key={
			'userID': user_id
		}
	)
	item = response.get('Item')
	if item:
		return {
			'statusCode': 200,
			'body': json.dumps(item)
		}
	else:
		return {
			'statusCode': 404,
			'body': json.dumps({'message': 'Participant not found'})
		}


def add_or_update_points(user_id, event_points):
	"""
	Adds points for a participant. If the participant does not exist, they are added.
	:param user_id: The ID of the participant
	:param event_points: The points to add to the participant's total
	:return: The response from DynamoDB after updating the item
	"""
	response = table.get_item(Key={'userID': user_id})

	if 'Item' in response:
		total_points = response['Item']['points'] + event_points
	else:
		total_points = event_points

	# Update the leaderboard
	table.put_item(
		Item={
			'userID': user_id,
			'points': total_points
		}
	)

	return {
		'statusCode': 200,
		'body': json.dumps({'message': f'User {user_id} now has {total_points} points'})
	}


def delete_participant(user_id):
	"""
	Delete a participant from the leaderboard
	:param user_id: The ID of the participant to delete
	:return: The response from DynamoDB after deleting the item
	"""
	table.delete_item(
		Key={
			'userID': user_id
		}
	)
	return {
		'statusCode': 200,
		'body': json.dumps({'message': f'User {user_id} deleted from leaderboard'})
	}
