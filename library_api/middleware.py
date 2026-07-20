# library_api/middleware.py

class SecurityHeadersMiddleware:
    """Injects strict security headers, keeping 'unsafe-inline' off API endpoints."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Allow inline scripts ONLY on docs pages so Swagger/ReDoc UI can render
        if request.path.startswith('/swagger') or request.path.startswith('/redoc'):
            script_src = "'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        else:
            # Strict XSS protection for all standard API/JSON routes
            script_src = "'self'"

        response['Content-Security-Policy'] = (
            f"default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            f"font-src 'self' https://fonts.gstatic.com data:; "
            f"img-src 'self' data: https:; "
            f"connect-src 'self' https:;"
        )

        return response