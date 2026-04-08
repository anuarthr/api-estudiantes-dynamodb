from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from notas import repository
from notas.serializers import NotaInputSerializer, NotaOutputSerializer


class NotasView(APIView):
    def post(self, request):
        serializer = NotaInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        nota = repository.create_nota(
            estudiante_id=data["estudiante_id"],
            codigo_materia=data["codigo_materia"],
            materia_nombre=data["materia_nombre"],
            nota=data["nota"],
        )
        return Response(NotaOutputSerializer(nota).data, status=status.HTTP_201_CREATED)


class NotasEstudianteView(APIView):
    def get(self, request, id):
        notas = repository.list_notas(id)
        return Response(NotaOutputSerializer(notas, many=True).data)


class NotaDetalleView(APIView):
    def get(self, request, id, codigo):
        nota = repository.get_nota(id, codigo)
        if not nota:
            return Response({"error": "Nota no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        return Response(NotaOutputSerializer(nota).data)
