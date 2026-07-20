class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Restrict sensitive features by default
        response['Permissions-Policy'] = "geolocation=(), microphone=(), camera=()"

        # Basic CSP (adjust directives as needed for your static/media files)
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"

        return response