# library_api/middleware.py

class SecurityHeadersMiddleware:
    """Injects modern security headers (Permissions-Policy & strict CSP) into all API responses."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 1. PERMISSIONS-POLICY
        # Explicitly disables unused browser APIs/hardware features for security audits
        response['Permissions-Policy'] = (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "camera=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "interest-cohort=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )

        # 2. CONTENT-SECURITY-POLICY
        # Strictly enforces 'self' without 'unsafe-inline' for API routes, allowing it only on docs
        if request.path.startswith('/swagger') or request.path.startswith('/redoc'):
            script_src = "'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        else:
            script_src = "'self'"

        response['Content-Security-Policy'] = (
            f"default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            f"font-src 'self' https://fonts.gstatic.com data:; "
            f"img-src 'self' data: https:; "
            f"connect-src 'self' https:;"
        )

        # 3. EXTRA HARDENING HEADERS
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response