from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserIDView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]

    def get(self, *args, **kwargs):
        users = [self.request.user.pk]
        return Response(users)


class UserDetail(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        user_id = self.kwargs.get('user_id')
        if user_id:
            return get_user_model().objects.filter(pk=user_id).\
                                            values('first_name',
                                                   'last_name',
                                                   'email')
        return get_user_model().objects.none() # pragma: no cover

    def get(self, *args, **kwargs):
        return Response(self.get_queryset().first())
