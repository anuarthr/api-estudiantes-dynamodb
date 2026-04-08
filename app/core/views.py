from rest_framework.response import Response
from rest_framework.views import APIView

from config import get_dynamodb_client, get_redis_client


class HealthView(APIView):
    def get(self, request):
        result = {"dynamodb": "ok", "redis": "ok"}

        try:
            get_dynamodb_client().list_tables()
        except Exception as e:
            result["dynamodb"] = f"error: {e}"

        try:
            get_redis_client().ping()
        except Exception as e:
            result["redis"] = f"error: {e}"

        return Response(result)
