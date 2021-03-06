from . import models
from .models import BTCTrade
from . import serializers
from .serializers import BTCTradeSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime

class BTCTradeList(APIView):
    def get(self, request, format=None):
        trades = BTCTrade.objects.all()
        serializer = BTCTradeSerializer(trades, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BTCTradeSerializer(data = request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, format=None):
    #     date_str = request.query_params.get('date', None)
    #     date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    #     if date is not None:
    #         items = RentPrice.objects.filter(date_value=date)
    #         items.delete()
    #         return Response(status = status.HTTP_204_NO_CONTENT)
    #     return Response("resource not found", status = status.HTTP_400_BAD_REQUEST)
