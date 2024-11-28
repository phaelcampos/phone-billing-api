from decimal import Decimal
from datetime import datetime, time, timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import CallRecord, ProcessedCall


class CallPricingService:
    STANDARD_RATE_START = time(6, 0)
    STANDARD_RATE_END = time(22, 0)
    FIXED_RATE = Decimal('0.36')
    STANDARD_MINUTE_RATE = Decimal('0.09')
    REDUCED_MINUTE_RATE = Decimal('0.00')

    @classmethod
    def calculate_price(cls, start_time: datetime, end_time: datetime) -> Decimal:
        price = cls.FIXED_RATE
        current_time = start_time

        while current_time < end_time:

            next_time = min(
                current_time.replace(
                    hour=22, minute=0, second=0, microsecond=0
                ) if current_time.time() < cls.STANDARD_RATE_END else
                current_time.replace(
                    hour=6, minute=0, second=0, microsecond=0
                ).replace(day=current_time.day + 1),
                end_time,
                (current_time + timedelta(minutes=1))
            )


            if (cls.STANDARD_RATE_START <= current_time.time() < cls.STANDARD_RATE_END):

                if (next_time - current_time).total_seconds() >= 60:
                    price += cls.STANDARD_MINUTE_RATE

            current_time = next_time

        return price.quantize(Decimal('0.01'))


class CallProcessingService:
    @staticmethod
    @transaction.atomic
    def process_call_records(call_id: str) -> ProcessedCall:
        start_record = CallRecord.objects.filter(
            call_id=call_id,
            type='start'
        ).first()

        end_record = CallRecord.objects.filter(
            call_id=call_id,
            type='end'
        ).first()

        if not (start_record and end_record):
            return None

        if end_record.timestamp <= start_record.timestamp:
            raise ValidationError("End time must be greater than start time")

        duration = end_record.timestamp - start_record.timestamp
        price = CallPricingService.calculate_price(
            start_record.timestamp,
            end_record.timestamp
        )

        processed_call, _ = ProcessedCall.objects.get_or_create(
            call_id=str(call_id),
            defaults={
                'source': start_record.source,
                'destination': start_record.destination,
                'start_time': start_record.timestamp,
                'end_time': end_record.timestamp,
                'duration': duration,
                'price': price
            }
        )

        return processed_call