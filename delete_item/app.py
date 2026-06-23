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

    if not item_id:
        return build_response(400, {
            "error": "Falta el id del item"
        })

    table.delete_item(Key={"id": item_id})

    return build_response(200, {
        "message": "Item eliminado correctamente",
        "id": item_id
    })