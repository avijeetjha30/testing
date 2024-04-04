import jwt
from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

#######################################################################
# Add rejson to control redis cache
# It used to blacklist the access token after logout and password reset
# https://gist.github.com/britisharmy/ca0c3e37be4b20ccf2f9fc802c52ed63
#######################################################################

redis_client = cache.client.get_client()


class GenerateToken:

    def __init__(self):
        pass

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        decodeJWT = jwt.decode(str(access), settings.SECRET_KEY, algorithms=['HS256'])

        decodeJWT['id'] = str(user.id) if user.id else ''
        decodeJWT['first_name'] = user.first_name
        decodeJWT['email'] = user.email

        encodeJWT = jwt.encode(decodeJWT, settings.SECRET_KEY)
        redis_client.sadd(f'user_{user.email}', decodeJWT['jti'])
        return {
            'access_token': str(encodeJWT),
            'refresh_token': str(refresh),
        }
