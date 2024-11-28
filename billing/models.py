from django.db import models
from django.core.validators import RegexValidator

class CallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('end', 'End'),
    )

    id = models.BigAutoField(primary_key=True)
    call_id = models.UUIDField(editable=True)
    type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()
    source = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^\d{11}$')],
        null=True,
        blank=True
    )
    destination = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^\d{11}$')],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'call_records'
        indexes = [
            models.Index(fields=['call_id']),
            models.Index(fields=['source']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Call {self.call_id} - {self.type}"

class ProcessedCall(models.Model):
    call_id = models.CharField(max_length=100, unique=True)
    source = models.CharField(max_length=11)
    destination = models.CharField(max_length=11)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'processed_calls'
        indexes = [
            models.Index(fields=['source']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]