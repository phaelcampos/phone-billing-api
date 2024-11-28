from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from .models import CallRecord, ProcessedCall
from .serializers import CallRecordSerializer
from .services import CallProcessingService


class CallRecordViewSet(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        call_record = serializer.save()

        if call_record.type == 'end':
            try:
                processed_call = CallProcessingService.process_call_records(
                    str(call_record.call_id)
                )
                if processed_call:
                    return Response({
                        "message": "Call processed successfully",
                        "call_details": {
                            "duration": str(processed_call.duration),
                            "price": float(processed_call.price),
                            "start_time": processed_call.start_time,
                            "end_time": processed_call.end_time
                        }
                    }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhoneBillView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='phone',
                description='Número de telefone do assinante',
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='period',
                description='Período (mês/ano) no formato YYYY-MM',
                required=False,
                type=str,
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    def get(self, request, phone):
        period = request.query_params.get('period')

        if not period:
            today = datetime.today()
            first_day = (today.replace(day=1) - relativedelta(months=1))
            period = first_day.strftime('%Y-%m')

        try:
            year, month = map(int, period.split('-'))
            first_day = datetime(year, month, 1)
            last_day = (first_day + relativedelta(months=1))
        except ValueError:
            return Response(
                {"error": "Formato de período inválido. Use YYYY-MM"},
                status=status.HTTP_400_BAD_REQUEST
            )

        calls = ProcessedCall.objects.filter(
            source=phone,
            end_time__gte=first_day,
            end_time__lt=last_day
        ).order_by('start_time')

        if not calls.exists():
            return Response(
                {"error": f"Nenhuma chamada encontrada para o número {phone} no período {period}"},
                status=status.HTTP_404_NOT_FOUND
            )

        total = calls.aggregate(total=Sum('price'))['total']

        formatted_calls = []
        for call in calls:
            duration_seconds = int(call.duration.total_seconds())
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60

            formatted_calls.append({
                'destination': call.destination,
                'call_date': call.start_time.strftime('%Y-%m-%d'),
                'call_time': call.start_time.strftime('%H:%M:%S'),
                'duration': f"{hours:02d}h{minutes:02d}m{seconds:02d}s",
                'price': f"R$ {call.price:.2f}"
            })

        response_data = {
            'subscriber': phone,
            'period': period,
            'total': f"R$ {total:.2f}",
            'calls': formatted_calls
        }

        return Response(response_data)