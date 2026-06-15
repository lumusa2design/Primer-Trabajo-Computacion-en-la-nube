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

    method = event.get("httpMethod")

    if not method:
        method = event.get("requestContext", {}).get("http", {}).get("method")

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

    return build_response(400, {
        "error": "Método o ruta no soportado",
        "method": method,
        "item_id": item_id
    })


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

    return build_response(201, {
        "message": "Item creado correctamente",
        "item": item
    })


def get_item(item_id):
    result = table.get_item(Key={"id": item_id})
    item = result.get("Item")

    if not item:
        return build_response(404, {
            "message": "Item no encontrado",
            "id": item_id
        })

    return build_response(200, item)


def get_all_items():
    result = table.scan()
    items = result.get("Items", [])

    return build_response(200, {
        "items": items
    })


def update_item(item_id, event):
    body = json.loads(event.get("body") or "{}")

    table.update_item(
        Key={"id": item_id},
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

    return build_response(200, {
        "message": "Item actualizado correctamente",
        "id": item_id
    })


def delete_item(item_id):
    table.delete_item(Key={"id": item_id})

    return build_response(200, {
        "message": "Item eliminado correctamente",
        "id": item_id
    })