from rest_framework import serializers
from .models import CallRecord, ProcessedCall
import uuid
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Start Call Example',
            value={
                'type': 'start',
                'timestamp': '2024-11-28T15:30:31.679Z',
                'source': '5544536483',
                'destination': '36053391352'
            }
        )
    ]
)
class CallRecordSerializer(serializers.ModelSerializer):
    call_id = serializers.UUIDField(required=False)

    class Meta:
        model = CallRecord
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        if data['type'] == 'start':
            data['call_id'] = uuid.uuid4()
            if not all([data.get('source'), data.get('destination')]):
                raise serializers.ValidationError(
                    "Source and destination are required for start records"
                )
        else:
            if not data.get('call_id'):
                raise serializers.ValidationError("End record must include call_id")

            try:
                start_record = CallRecord.objects.get(
                    call_id=data['call_id'],
                    type='start'
                )

                if data['timestamp'] <= start_record.timestamp:
                    raise serializers.ValidationError(
                        "End time must be greater than start time"
                    )
            except CallRecord.DoesNotExist:
                raise serializers.ValidationError(
                    f"No start record found for call_id {data['call_id']}"
                )

        return data
