class SecurityHeadersMiddleware:
    #Injects modern missing security headers (CSP & Permissions-Policy)"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy (allows inline scripts/styles for Swagger & Redoc)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:;"
        )

        # Permissions Policy
        response['Permissions-Policy'] = "geolocation=(), microphone=(), camera=(), payment=()"

        return response