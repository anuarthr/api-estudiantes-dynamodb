import os
from decimal import Decimal

from boto3.dynamodb.types import TypeDeserializer

from config import get_dynamodb_client

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "estudiantes")

_deserializer = TypeDeserializer()


def _deserialize(item: dict) -> dict:
    raw = {k: _deserializer.deserialize(v) for k, v in item.items()}
    return _fix_decimals(raw)


def _fix_decimals(obj):
    """Convierte Decimal (devuelto por TypeDeserializer) a float para JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _fix_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fix_decimals(i) for i in obj]
    return obj


def create_perfil(id: str, nombre_completo: str, correo_institucional: str) -> dict:
    client = get_dynamodb_client()
    item = {
        "pk": {"S": f"EST#{id}"},
        "sk": {"S": "PERFIL"},
        "nombre_completo": {"S": nombre_completo},
        "correo_institucional": {"S": correo_institucional},
    }
    client.put_item(TableName=TABLE_NAME, Item=item)
    return _deserialize(item)


def get_perfil(id: str) -> dict | None:
    client = get_dynamodb_client()
    response = client.get_item(
        TableName=TABLE_NAME,
        Key={
            "pk": {"S": f"EST#{id}"},
            "sk": {"S": "PERFIL"},
        },
    )
    item = response.get("Item")
    return _deserialize(item) if item else None


def list_perfiles() -> list[dict]:
    client = get_dynamodb_client()
    response = client.scan(
        TableName=TABLE_NAME,
        FilterExpression="sk = :sk",
        ExpressionAttributeValues={":sk": {"S": "PERFIL"}},
    )
    return [_deserialize(item) for item in response.get("Items", [])]


def delete_perfil(id: str) -> None:
    client = get_dynamodb_client()
    client.delete_item(
        TableName=TABLE_NAME,
        Key={
            "pk": {"S": f"EST#{id}"},
            "sk": {"S": "PERFIL"},
        },
    )
