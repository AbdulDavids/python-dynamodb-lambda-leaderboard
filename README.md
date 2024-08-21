# Leaderboard Manager

This project implements a leaderboard management system using AWS Lambda and DynamoDB. It includes functions for adding/updating points, retrieving the leaderboard, and managing participants. The project uses AWS SAM CLI for local development and testing.


## Prerequisites

Ensure you have the following installed on your system:

- **AWS CLI**: [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **AWS SAM CLI**: [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Docker**: Required for running DynamoDB locally. [Installation Guide](https://docs.docker.com/get-docker/)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<repo-link>
cd leaderboard-manager
```

### 2. Install AWS SAM CLI

If not installed, follow the official [AWS SAM CLI Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) to set it up.

## Running DynamoDB Locally

To simulate the DynamoDB environment locally, you need to run DynamoDB Local using Docker:

```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

## Creating the DynamoDB Table Locally

After running DynamoDB locally, you need to create the `Leaderboard` table:

```bash
aws dynamodb create-table \
    --table-name Leaderboard \
    --attribute-definitions AttributeName=userID,AttributeType=S \
    --key-schema AttributeName=userID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000
```

## Testing Locally with SAM CLI

### 1. **Update the Code for Local Testing**

Ensure the `app.py` file is configured to point to your local DynamoDB instance:

```python
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
```

### 2. **Run the Lambda Function Locally**

Use the SAM CLI to invoke your Lambda function locally. Start by creating test event files in the `events/` directory.

#### Example: Add Points

```bash
sam local invoke "LeaderboardFunction" -e events/add_points_event.json
```

### 3. **Test with API Gateway Locally**

To test your Lambda function with API Gateway locally, start the API server:

```bash
sam local start-api
```

You can now send HTTP requests to the API using tools like `curl` or Postman.

#### Example: Add Points with `curl`

```bash
curl --request POST --url http://localhost:3000/points --data '{"userID": "user123", "points": 18}'
```

## API Endpoints

When running the API locally, the following endpoints are available:

- **POST /points**: Add or update points for a participant.
- **GET /leaderboard**: Retrieve the top participants in the leaderboard.
- **GET /participant/{userID}**: Get points for a specific participant.
- **DELETE /participant/{userID}**: Delete a participant from the leaderboard.

## Deploying to AWS

Once you’ve tested your Lambda function locally and it’s working as expected, you can deploy it to AWS using the following commands:

```bash
sam build
sam deploy --guided
```

The `--guided` option helps you set up your deployment configuration, such as stack name, region, and other parameters.
