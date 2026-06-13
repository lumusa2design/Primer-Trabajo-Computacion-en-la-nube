import json
import uuid
import os

from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key


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
    method = event.get("httpMethod")
    path_parameters = event.get("pathParameters") or {}
    item_id = path_parameters.get("id")

    if method == "OPTIONS":
        return build_response(200, {"message": "CORS OK"})

    if method == "POST":
        return create_item(event)

    if method == "GET" and item_id:
        return get_item(item_id)

    if method == "GET":
        return get_all_items()

    if method == "PUT" and item_id:
        return update_item(item_id, event)

    if method == "DELETE" and item_id:
        return delete_item(item_id)

    return build_response(400, {"error": "Método o ruta no soportado"})


def create_item(event):

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

    return build_response(
        201,
        {
            "message": "Item creado correctamente",
            "item": item
        }
    )


def get_item(item_id):

    response = table.get_item(
        Key={
            "id": item_id
        }
    )

    item = response.get("Item")

    if not item:
        return build_response(
            404,
            {
                "message": "Item no encontrado"
            }
        )

    return build_response(
        200,
        item
    )

def get_all_items():

    response = table.scan()

    items = response.get("Items", [])

    return build_response(
        200,
        items
    )


def update_item(item_id, event):

    body = json.loads(event.get("body") or "{}")

    table.update_item(
        Key={
            "id": item_id
        },
        UpdateExpression="""
            SET #n = :n,
                description = :d,
                category = :c,
                updatedAt = :u
        """,
        ExpressionAttributeNames={
            "#n": "name"
        },
        ExpressionAttributeValues={
            ":n": body.get("name"),
            ":d": body.get("description"),
            ":c": body.get("category"),
            ":u": get_now()
        }
    )

    return build_response(
        200,
        {
            "message": "Item actualizado correctamente"
        }
    )


def delete_item(item_id):

    table.delete_item(
        Key={
            "id": item_id
        }
    )

    return build_response(
        200,
        {
            "message": "Item eliminado correctamente"
        }
    )