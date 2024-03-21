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
        by_user = request.query_params.get('by_user') == 'true'

        if category:
            self.queryset = self.queryset.filter(category__name=category)

        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)
            
        if quantity:
            self.queryset = self.queryset[: int(quantity)]


        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)