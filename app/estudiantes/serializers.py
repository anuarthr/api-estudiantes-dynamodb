from rest_framework import serializers


class EstudianteInputSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=20)
    nombre_completo = serializers.CharField(max_length=100)
    correo_institucional = serializers.EmailField()


class EstudianteOutputSerializer(serializers.Serializer):
    pk = serializers.CharField()
    sk = serializers.CharField()
    nombre_completo = serializers.CharField()
    correo_institucional = serializers.CharField()
