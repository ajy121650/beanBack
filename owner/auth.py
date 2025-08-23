from rest_framework_simplejwt.authentication import JWTAuthentication

# Django REST Framework에서 JWT 토큰을 쿠키(access_token) 또는 Authorization 헤더에서 읽어 인증하는 커스텀 인증 클래스
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        raw = self.get_raw_token(header) if header else request.COOKIES.get('access_token')
        if not raw:
            return None
        try:
            validated = self.get_validated_token(raw)
        except Exception:
            return None
        return self.get_user(validated), validated
