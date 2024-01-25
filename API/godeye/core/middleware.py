import logging

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.jwt_auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()
        query_string = scope["query_string"]
        query_string = query_string.decode()
        if "access_token" in query_string:
            try:
                token = query_string.split("=")[1]
                access_token = AccessToken(token)
                user = await sync_to_async(get_user_model)()
                scope["user"] = await sync_to_async(user.objects.get)(
                    id=access_token["user_id"]
                )
            except Exception as err:
                logger.info(HTTP_404_NOT_FOUND(err))
        return await super().__call__(scope, receive, send)
