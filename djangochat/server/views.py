from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from .serializer import ServerSerializer
from .models import Server


class ServerListView(viewsets.ViewSet):

    queryset = Server.objects.all()

    def list(self, request):
        category = request.query_params.get('category')
        quantity = request.query_params.get('qty')

        if category:
            self.queryset = self.queryset.filter(category__name=category)

        if quantity:
            self.queryset = self.queryset[: int(quantity)]

        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)