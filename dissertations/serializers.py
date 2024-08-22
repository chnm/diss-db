from rest_framework import serializers
from dissertations.models import Scholar


class ScholarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholar
        fields = ["id", "name_first", "name_middle", "name_last", "name_suffix"]
