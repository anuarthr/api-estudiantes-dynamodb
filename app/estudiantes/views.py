from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from estudiantes import repository, services
from estudiantes.serializers import EstudianteInputSerializer, EstudianteOutputSerializer


class EstudiantesListView(APIView):
    def get(self, request):
        perfiles = repository.list_perfiles()
        return Response(EstudianteOutputSerializer(perfiles, many=True).data)

    def post(self, request):
        serializer = EstudianteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        perfil = repository.create_perfil(
            id=data["id"],
            nombre_completo=data["nombre_completo"],
            correo_institucional=data["correo_institucional"],
        )
        return Response(EstudianteOutputSerializer(perfil).data, status=status.HTTP_201_CREATED)


class EstudianteDetailView(APIView):
    def get(self, request, id):
        perfil = services.get_perfil_cached(id)
        if not perfil:
            return Response({"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EstudianteOutputSerializer(perfil).data)

    def delete(self, request, id):
        if not repository.get_perfil(id):
            return Response({"error": "Estudiante no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        repository.delete_perfil(id)
        services.invalidate_cache(id)
        return Response(status=status.HTTP_204_NO_CONTENT)
