from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from datetime import timedelta

class SessionRefreshMiddleware:
    """
    Middleware to refresh user sessions periodically to prevent timeout during active use.
    This middleware updates a timestamp in the session data at specified intervals,
    effectively extending the session's lifetime as long as the user is active.

    Configuration options (can be set in Django settings):
    - SESSION_REFRESH_KEY: The session key to store the last refresh timestamp. Default is 'last_session_refresh'.
    - SESSION_REFRESH_INTERVAL: The interval in seconds to refresh the session. Default is 86400 (24 hours).
    - SESSION_REFRESH_SKIP_STAFF_USERS: If True, skips session refresh for is_staff users. Default is False.
    - SESSION_REFRESH_SKIP_SUPERUSER_USERS: If True, skips session refresh for is_superuser users. Default is True.
    - SESSION_REFRESH_SKIP_STATIC_AND_MEDIA: If True, skips session refresh for static and media file requests. Default is True.
    - SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS: If True, skips session refresh for unauthenticated users. Default is True.
    """

    _SESSION_REFRESH_KEY = "last_session_refresh"
    _SESSION_REFRESH_INTERVAL = 86400  # 24 hours in seconds
    _SESSION_REFRESH_SKIP_STAFF_USERS = False
    _SESSION_REFRESH_SKIP_SUPERUSER_USERS = True
    _SESSION_REFRESH_SKIP_STATIC_AND_MEDIA = True
    _SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS = True

    def __init__(self, get_response):
        self._SESSION_REFRESH_KEY = getattr(settings, "SESSION_REFRESH_KEY", self._SESSION_REFRESH_KEY)
        self._SESSION_REFRESH_INTERVAL = getattr(settings, "SESSION_REFRESH_INTERVAL", self._SESSION_REFRESH_INTERVAL)
        self._SESSION_REFRESH_SKIP_STAFF_USERS = getattr(settings, "SESSION_REFRESH_SKIP_STAFF_USERS", self._SESSION_REFRESH_SKIP_STAFF_USERS)
        self._SESSION_REFRESH_SKIP_SUPERUSER_USERS = getattr(settings, "SESSION_REFRESH_SKIP_SUPERUSER_USERS", self._SESSION_REFRESH_SKIP_SUPERUSER_USERS)
        self._SESSION_REFRESH_SKIP_STATIC_AND_MEDIA = getattr(settings, "SESSION_REFRESH_SKIP_STATIC_AND_MEDIA", self._SESSION_REFRESH_SKIP_STATIC_AND_MEDIA)
        self._SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS = getattr(settings, "SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS", self._SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS)

        self.get_response = get_response
        self.refresh_delta = timedelta(seconds=self._SESSION_REFRESH_INTERVAL)

    def __call__(self, request):
        response = self.get_response(request)

        if self._should_skip_url(request):
            return response

        if self._should_skip_user(request):
            return response

        if self._should_refresh_session(request):
            request.session[self._SESSION_REFRESH_KEY] = timezone.now().isoformat()
            request.session.modified = True

        return response

    def _should_skip_url(self, request) -> bool:
        if not self._SESSION_REFRESH_SKIP_STATIC_AND_MEDIA:
            return False

        path = request.path or ""
        static_url = getattr(settings, "STATIC_URL", "/static/") or "/static/"
        media_url = getattr(settings, "MEDIA_URL", None)

        if static_url and static_url != "/" and path.startswith(static_url):
            return True

        if media_url and media_url != "/" and path.startswith(media_url):
            return True

        return False

    def _should_skip_user(self, request) -> bool:
        user = getattr(request, "user", None)
        if self._SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS and not getattr(user, "is_authenticated", False):
            return True
        if self._SESSION_REFRESH_SKIP_SUPERUSER_USERS and getattr(user, "is_superuser", False):
            return True
        if self._SESSION_REFRESH_SKIP_STAFF_USERS and getattr(user, "is_staff", False):
            return True
        return False

    def _should_refresh_session(self, request) -> bool:
        last_refresh_raw = request.session.get(self._SESSION_REFRESH_KEY)
        if not last_refresh_raw:
            return True

        last_refresh = parse_datetime(last_refresh_raw)
        if last_refresh is None:
            return True

        now = timezone.now()
        return now - last_refresh >= self.refresh_delta
