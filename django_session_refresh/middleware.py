from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from datetime import timedelta

class SessionRefreshMiddleware:
    """
    Middleware to refresh user sessions periodically to prevent timeout during active use.
    This middleware updates a timestamp in the session data at specified intervals,
    effectively extending the session's lifetime as long as the user is active.

    Configuration dictionary options (can be set in Django settings):
    ```python
    DJANGO_SESSION_REFRESH = {
        'REFRESH_INTERVAL': 86400,  # 24 hours in seconds
        'SESSION_KEY_NAME': 'django_session_refreshed_at',
        'REQUEST_ATTR_NAME': 'django_session_refresh',
        'SKIP_STAFF_USERS': False,
        'SKIP_SUPERUSER_USERS': True,
        'SKIP_STATIC_AND_MEDIA': True,
        'SKIP_UNAUTHENTICATED_USERS': True,
    }
    ```

    After a successful session refresh, the middleware adds the following dictionary attribute to the `request` object:
    - `request.django_session_refresh['refreshed']`
    - `request.django_session_refresh['refreshed_at']`
    """

    _REFRESH_INTERVAL = 86400  # 24 hours in seconds
    _SESSION_KEY_NAME = 'django_session_refreshed_at'
    _REQUEST_ATTR_NAME = 'django_session_refresh'
    _SKIP_STAFF_USERS = False
    _SKIP_SUPERUSER_USERS = True
    _SKIP_STATIC_AND_MEDIA = True
    _SKIP_UNAUTHENTICATED_USERS = True

    def __init__(self, get_response):
        SETTINGS = getattr(settings, 'DJANGO_SESSION_REFRESH', {})
        self._REFRESH_INTERVAL = SETTINGS.get('REFRESH_INTERVAL', self._REFRESH_INTERVAL)
        self._SESSION_KEY_NAME = SETTINGS.get('SESSION_KEY_NAME', self._SESSION_KEY_NAME)
        self._REQUEST_ATTR_NAME = SETTINGS.get('REQUEST_ATTR_NAME', self._REQUEST_ATTR_NAME)
        self._SKIP_STAFF_USERS = SETTINGS.get('SKIP_STAFF_USERS', self._SKIP_STAFF_USERS)
        self._SKIP_SUPERUSER_USERS = SETTINGS.get('SKIP_SUPERUSER_USERS', self._SKIP_SUPERUSER_USERS)
        self._SKIP_STATIC_AND_MEDIA = SETTINGS.get('SKIP_STATIC_AND_MEDIA', self._SKIP_STATIC_AND_MEDIA)
        self._SKIP_UNAUTHENTICATED_USERS = SETTINGS.get('SKIP_UNAUTHENTICATED_USERS', self._SKIP_UNAUTHENTICATED_USERS)

        self.get_response = get_response
        self.refresh_delta = timedelta(seconds=self._REFRESH_INTERVAL)

    def __call__(self, request):
        if self._should_skip_url(request):
            return self.get_response(request)

        if self._should_skip_user(request):
            return self.get_response(request)

        if self._should_refresh_session(request):
            request.session[self._SESSION_KEY_NAME] = timezone.now().isoformat()
            request.session.modified = True
            setattr(request, self._REQUEST_ATTR_NAME, {
                'refreshed': True,
                'refreshed_at': timezone.now(),
            })

        return self.get_response(request)

    def _should_skip_url(self, request) -> bool:
        if not self._SKIP_STATIC_AND_MEDIA:
            return False

        path = request.path or ''
        static_url = getattr(settings, 'STATIC_URL', '/static/') or '/static/'
        media_url = getattr(settings, 'MEDIA_URL', None)

        if static_url and static_url != '/' and path.startswith(static_url):
            return True

        if media_url and media_url != '/' and path.startswith(media_url):
            return True

        return False

    def _should_skip_user(self, request) -> bool:
        user = getattr(request, 'user', None)
        if self._SKIP_UNAUTHENTICATED_USERS and not getattr(user, 'is_authenticated', False):
            return True
        if self._SKIP_SUPERUSER_USERS and getattr(user, 'is_superuser', False):
            return True
        if self._SKIP_STAFF_USERS and getattr(user, 'is_staff', False):
            return True
        return False

    def _should_refresh_session(self, request) -> bool:
        last_refresh_raw = request.session.get(self._SESSION_KEY_NAME)
        if not last_refresh_raw:
            return True

        last_refresh = parse_datetime(last_refresh_raw)
        if last_refresh is None:
            return True

        now = timezone.now()
        return now - last_refresh >= self.refresh_delta
