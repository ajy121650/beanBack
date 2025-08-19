from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        raw = self.get_raw_token(header) if header else request.COOKIES.get('access_token')
        if not raw:
            return None
        try:
            validated = self.get_validated_token(raw)
        except Exception:
            # ❗️만료/깨진 토큰이면 401 던지지 말고 조용히 패스
            return None
        return self.get_user(validated), validated
