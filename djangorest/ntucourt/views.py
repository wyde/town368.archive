from django.shortcuts import render

# Create your views here.
from ntucourt.models import Report, Station
from ntucourt.serializers import ReportSerializer, StationSerializer
from rest_framework import viewsets
#from rest_framework import generics


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = Report.objects.all()
    serializer_class = ReportSerializer
    def get_queryset(self):
        queryset = Report.objects.all()
        record_t = self.request.query_params.get('record_t', None)
        if record_t is not None:
            queryset = queryset.filter(record_t=record_t)
        return queryset

class StationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
