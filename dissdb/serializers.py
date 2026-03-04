from rest_framework import serializers
from dissdb.models import Scholar


class ScholarSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    aha_scholar_id = serializers.IntegerField(read_only=True)
    name_full = serializers.CharField(read_only=True)


class ScholarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholar
        fields = ["name_first", "name_middle", "name_last", "name_suffix"]
