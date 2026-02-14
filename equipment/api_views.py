from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Equipment, EquipmentStatus
from .serializers import EquipmentSerializer, EquipmentStatusSerializer, CommandSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    """REST API for equipment CRUD + status + commands."""
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        eq = self.get_object()
        logs = eq.status_logs.all()[:20]
        serializer = EquipmentStatusSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def command(self, request, pk=None):
        """Send command to equipment (demo: just log it)."""
        eq = self.get_object()
        ser = CommandSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # In production: forward to actual equipment via protocol
        EquipmentStatus.objects.create(
            equipment=eq,
            status="running",
            message=f"Command: {ser.validated_data['command']}",
            metadata=ser.validated_data.get("parameters", {}),
        )
        return Response({"status": "command_sent", "equipment": eq.name})

    @action(detail=True, methods=["post"])
    def report_status(self, request, pk=None):
        """Endpoint for equipment to report its status."""
        eq = self.get_object()
        st = request.data.get("status", "idle")
        meta = request.data.get("metadata", {})
        EquipmentStatus.objects.create(equipment=eq, status=st, metadata=meta)
        return Response({"received": True})


class EquipmentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentStatus.objects.select_related("equipment").all()
    serializer_class = EquipmentStatusSerializer
