from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class CurrentUserIDView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        users = [self.request.user.pk]
        return users

    def get(self, *args, **kwargs):
        return Response(self.get_queryset())
