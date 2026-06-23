import json
import os

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


def lambda_handler(event, context):
    print(json.dumps(event))

    path_parameters = event.get("pathParameters") or {}
    item_id = path_parameters.get("id")

    if item_id:
        return get_item(item_id)

    return get_all_items()


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