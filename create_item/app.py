import json
import uuid
import os
from datetime import datetime, timezone

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "Items")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }


def get_now():
    return datetime.now(timezone.utc).isoformat()


def lambda_handler(event, context):
    print(json.dumps(event))

    body = json.loads(event.get("body") or "{}")

    item = {
        "id": str(uuid.uuid4()),
        "name": body.get("name"),
        "description": body.get("description"),
        "category": body.get("category", "general"),
        "createdAt": get_now(),
        "updatedAt": get_now()
    }

    table.put_item(Item=item)

    return build_response(201, {
        "message": "Item creado correctamente",
        "item": item
    })