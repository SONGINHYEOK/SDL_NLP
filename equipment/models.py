from django.db import models


class Equipment(models.Model):
    """Lab instrument connected via REST/MQTT/OPC-UA."""

    class EquipmentType(models.TextChoices):
        LIQUID_HANDLER = "liquid_handler", "Liquid Handler"
        MICROFLUIDIC = "microfluidic", "Microfluidic Mixer"
        DLS = "dls", "Dynamic Light Scattering"
        PLATE_READER = "plate_reader", "Plate Reader"
        HPLC = "hplc", "HPLC"
        CENTRIFUGE = "centrifuge", "Centrifuge"

    class Protocol(models.TextChoices):
        REST_API = "rest_api", "REST API"
        MQTT = "mqtt", "MQTT"
        OPCUA = "opcua", "OPC-UA"
        SERIAL = "serial", "Serial"
        MANUAL = "manual", "Manual"

    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=30, choices=EquipmentType.choices)
    manufacturer = models.CharField(max_length=200, blank=True, default="")
    model_number = models.CharField(max_length=200, blank=True, default="")

    # Connection
    protocol = models.CharField(max_length=20, choices=Protocol.choices, default=Protocol.REST_API)
    endpoint_url = models.CharField(max_length=500, blank=True, default="")
    api_key = models.CharField(max_length=500, blank=True, default="")
    is_connected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"


class EquipmentStatus(models.Model):
    """Time-series status log for equipment monitoring."""

    class Status(models.TextChoices):
        IDLE = "idle", "Idle"
        RUNNING = "running", "Running"
        ERROR = "error", "Error"
        MAINTENANCE = "maintenance", "Maintenance"
        OFFLINE = "offline", "Offline"

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="status_logs")
    status = models.CharField(max_length=20, choices=Status.choices)
    metadata = models.JSONField(default=dict, blank=True, help_text="Temperature, humidity, etc.")
    message = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"

    def __str__(self):
        return f"{self.equipment.name}: {self.status} @ {self.timestamp}"
