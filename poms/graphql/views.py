# api/views.py
from django.http import JsonResponse
from strawberry.django.views import GraphQLView

from poms.common.authentication import JWTAuthentication, KeycloakAuthentication
from poms.users.utils import get_master_user_and_member

AUTHENTICATORS = (
    JWTAuthentication(),
    KeycloakAuthentication(),
)


class AuthGraphQLView(GraphQLView):
    def _authenticate(self, request):
        # Try each authenticator, same idea as DRF
        for authenticator in AUTHENTICATORS:
            result = authenticator.authenticate(request)
            if result:
                user, auth = result
                request.user = user
                request.auth = auth
                return user
        return getattr(request, "user", None)

    def dispatch(self, request, *args, **kwargs):
        user = self._authenticate(request)

        member, master_user = get_master_user_and_member(request)

        request.user.member = member
        request.user.master_user = master_user

        # If you want /graphql to require auth for EVERYTHING:
        if not user or not getattr(user, "is_authenticated", False):
            return JsonResponse(
                {"data": None, "errors": [{"message": "Not authenticated"}]},
                status=401,
            )

        return super().dispatch(request, *args, **kwargs)
