from rest_framework.authentication import SessionAuthentication


class AlwaysCSRFSessionAuthentication(SessionAuthentication):
    """
    The normal session auth doesn't check csrf if there's no logged
    in user. This fixes that.
    """

    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """
        self.enforce_csrf(request)

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'user', None)

        if not user or not user.is_active:
            return None

        # CSRF passed with authenticated user
        return (user, None)
