from rest_framework import serializers
from dissdb.models import Scholar


class ScholarSerializer(serializers.Serializer):
    aha_scholar_id = serializers.IntegerField(read_only=True)
    name_full = serializers.CharField(read_only=True)
