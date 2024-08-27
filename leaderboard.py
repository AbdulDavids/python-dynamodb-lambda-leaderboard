import json
import psycopg2
import os
from psycopg2.extras import RealDictCursor

NEON_DB_URL = os.environ['NEON_DB_URL']

def get_db_connection():
	return psycopg2.connect(NEON_DB_URL, cursor_factory=RealDictCursor)


def lambda_handler(event, context):
	"""
    Entry point for the Lambda function to handle different API requests
    """
	print(f'Event: {event}')
	print(f'Context: {context}')
	print(f'NEON_DB_URL: {NEON_DB_URL}
	try:

		http_method = event['requestContext']['http']['method']
		path = event['requestContext']['http']['path']

		print(f'HTTP method: {http_method}')
		print(f'Path: {path}')

		print(f'Event: {event}')
		print(f'Context: {context}')

		if http_method == 'POST' and path == '/points':
			body = json.loads(event['body'])
			user_id = body['userID']
			points_to_add = body['points']
			print(f'Adding {points_to_add} points for user {user_id}')
			return add_points(user_id, points_to_add)

		elif http_method == 'GET' and path == '/leaderboard':
			query_params = event.get('queryStringParameters', {}) or {}
			limit = int(query_params.get('limit', 10))
			return get_leaderboard(limit)

		elif http_method == 'GET' and path.startswith('/participant/'):
			user_id = event['pathParameters']['userID']
			return get_participant_points(user_id)

		elif http_method == 'DELETE' and path.startswith('/participant/'):
			user_id = event['pathParameters']['userID']
			return delete_participant(user_id)

		elif http_method == 'GET':
			print("Welcome to the Leaderboard API")
			return {
				'statusCode': 200,
				'body': json.dumps({'message': 'Welcome to the Leaderboard API'})
			}

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

	print(f"Getting leaderboard with limit {limit}")
	try:
		with get_db_connection() as conn:
			with conn.cursor() as cur:
				cur.execute("SELECT * FROM leaderboard ORDER BY points DESC LIMIT %s", (limit,))
				items = cur.fetchall()
	except Exception as e:
		print(f"Error getting leaderboard: {e}")
		return {
			'statusCode': 500,
			'body': json.dumps({'message': str(e)})
		}

	return {
		'statusCode': 200,
		'body': json.dumps(items)
	}


def get_participant_points(user_id):
	"""
    Get the points for a participant
    :param user_id: The ID of the participant
    :return: The participant's points and details
    """
	with get_db_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM leaderboard WHERE user_id = %s", (user_id,))
			item = cur.fetchone()

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


def add_points(user_id, points_to_add):
	"""
    Adds points to a participant's total. If the participant does not exist, they are added with the given points.
    :param user_id: The ID of the participant
    :param points_to_add: The points to add to the participant's total
    :return: The response after updating the points
    """
	print(f"Adding {points_to_add} points for user {user_id}")

	with get_db_connection() as conn:
		with conn.cursor() as cur:
			# First, try to update an existing record
			cur.execute("""
                UPDATE leaderboard
                SET points = points + %s
                WHERE user_id = %s
                RETURNING points
            """, (points_to_add, user_id))

			result = cur.fetchone()

			if result is None:
				# If no existing record, insert a new one
				cur.execute("""
                    INSERT INTO leaderboard (user_id, points)
                    VALUES (%s, %s)
                    RETURNING points
                """, (user_id, points_to_add))
				result = cur.fetchone()

			conn.commit()
			new_total = result['points']

	print(f'User {user_id} now has {new_total} points')

	return {
		'statusCode': 200,
		'body': json.dumps({'message': f'User {user_id} now has {new_total} points'})
	}


def delete_participant(user_id):
	"""
    Delete a participant from the leaderboard
    :param user_id: The ID of the participant to delete
    :return: The response after deleting the participant
    """
	with get_db_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM leaderboard WHERE user_id = %s", (user_id,))
			conn.commit()

	return {
		'statusCode': 200,
		'body': json.dumps({'message': f'User {user_id} deleted from leaderboard'})
	}
