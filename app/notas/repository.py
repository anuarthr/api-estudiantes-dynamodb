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


def create_nota(estudiante_id: str, codigo_materia: str, materia_nombre: str, nota: float) -> dict:
    client = get_dynamodb_client()
    item = {
        "pk": {"S": f"EST#{estudiante_id}"},
        "sk": {"S": f"NOTA#{codigo_materia}"},
        "materia_nombre": {"S": materia_nombre},
        "nota": {"N": str(nota)},
    }
    client.put_item(TableName=TABLE_NAME, Item=item)
    return _deserialize(item)


def get_nota(estudiante_id: str, codigo_materia: str) -> dict | None:
    client = get_dynamodb_client()
    response = client.get_item(
        TableName=TABLE_NAME,
        Key={
            "pk": {"S": f"EST#{estudiante_id}"},
            "sk": {"S": f"NOTA#{codigo_materia}"},
        },
    )
    item = response.get("Item")
    return _deserialize(item) if item else None


def list_notas(estudiante_id: str) -> list[dict]:
    client = get_dynamodb_client()
    response = client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression="pk = :pk AND begins_with(sk, :prefix)",
        ExpressionAttributeValues={
            ":pk": {"S": f"EST#{estudiante_id}"},
            ":prefix": {"S": "NOTA#"},
        },
    )
    return [_deserialize(item) for item in response.get("Items", [])]
