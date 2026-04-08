import os

import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "dynamodb",
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
)

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "estudiantes")


def create_table():
    existing = client.list_tables()["TableNames"]
    if TABLE_NAME in existing:
        print(f"La tabla '{TABLE_NAME}' ya existe.")
        return

    client.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"Tabla '{TABLE_NAME}' creada exitosamente.")


if __name__ == "__main__":
    create_table()
