from rest_framework import serializers


class NotaInputSerializer(serializers.Serializer):
    estudiante_id = serializers.CharField(max_length=20)
    codigo_materia = serializers.CharField(max_length=20)
    materia_nombre = serializers.CharField(max_length=100)
    nota = serializers.FloatField(min_value=0, max_value=10)


class NotaOutputSerializer(serializers.Serializer):
    pk = serializers.CharField()
    sk = serializers.CharField()
    materia_nombre = serializers.CharField()
    nota = serializers.FloatField()
