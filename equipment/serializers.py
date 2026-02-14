from rest_framework import serializers
from .models import Equipment, EquipmentStatus


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = "__all__"


class EquipmentStatusSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = EquipmentStatus
        fields = "__all__"


class CommandSerializer(serializers.Serializer):
    """Send command to equipment."""
    equipment_id = serializers.IntegerField()
    command = serializers.CharField()
    parameters = serializers.JSONField(required=False, default=dict)
