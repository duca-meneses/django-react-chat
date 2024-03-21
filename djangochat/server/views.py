from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from django.db.models import Count

from .serializer import ServerSerializer
from .models import Server


class ServerListView(viewsets.ViewSet):

    queryset = Server.objects.all()

    def list(self, request):
        '''Return a List of servers filtered by various parameters.

        This method retrieves a list of servers based on various optional query parameters provided
        in the request. The available query parameters include:

        - `category` (str): Filter servers by category name.
        - `qty` (int): Limit the number of servers returned.
        - `by_user` (bool): Filter servers by the currently authenticated user if set to 'true'.
        - `by_serverid` (int): Filter servers by a specific server ID.
        - `with_num_members` (bool): Annotate the queryset with the number of members if set to 'true'.

        Args:
            request: A Django Request object containing query parameters.

        Returns:
            A queryset of servers filtered by the specified parameters.
            
        Raises:
            AuthenticationFailed: If the query includes the 'by_user' or 'by_serverid'
                parameters an the user is not authenticated
            ValidationError: If there is an error parsing or validating the query parameters.
                this can occur if the `by_serverid` parameter is not a valid integer, or if the
                server with the specified ID does not exist.
            
        Examples:
        To retrieve all servers in the 'gaming' category with at least 5 members, you can make
        the following request

            GET /api/server/select/?category=gaming&with_members=true

        To retrieve the first 5 servers that the authenticated user is a member of, you can make
        the following request:

            GET /api/server/select/?by_user=true&qty=5
        '''
        category = request.query_params.get('category')
        quantity = request.query_params.get('qty')
        by_user = request.query_params.get('by_user') == 'true'
        by_serverid = request.query_params.get('by_serverid')
        with_num_members = request.query_params.get('with_num_members') == 'true'

        if by_user or by_serverid and not request.user.is_authenticated:
            raise AuthenticationFailed()
        
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count('member'))
            
        if quantity:
            self.queryset = self.queryset[: int(quantity)]

        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f'Server with id {by_serverid} not found')
            except ValueError:
                raise ValidationError(detail='Server value error')

        serializer = ServerSerializer(self.queryset, many=True, context={'num_members': with_num_members})
        return Response(serializer.data)