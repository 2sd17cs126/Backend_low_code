from dataclasses import field
from rest_framework import serializers

from Orthogonal_array.models import Array


class ArrayModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Array
        fields=('table')