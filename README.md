# django-session-refresh
A simple Django middleware to refresh user sessions periodically (24h by default) to prevent timeout during user activity.

This middleware updates a timestamp in the session data at specified intervals, effectively extending the session's lifetime as long as the user is active.

* Since this middleware depends on user information, it should be placed after Django's `AuthenticationMiddleware` in the middleware stack.

## Installation
1. Run `pip install django-session-refresh`
2. Add `django_session_refresh.middleware.SessionRefreshMiddleware` to `settings.py` ass bellow

```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Django default AuthenticationMiddleware
    'django_session_refresh.middleware.SessionRefreshMiddleware',  # django-session-refresh
    ...
]
```

## Configuration (optional)
The dictionary settings bellow are optional and if not defined in `settings.py` the default values will be used.

```python
DJANGO_SESSION_REFRESH = {
    # The interval in seconds to refresh the session
    'REFRESH_INTERVAL': 86400,  # 24 hours in seconds

    # The name of the session key to store the last refresh timestamp
    'SESSION_KEY_NAME': 'django_session_refreshed_at',

    # The name of the request attribute to store session refresh information
    'REQUEST_ATTR_NAME': 'django_session_refresh',

    # Skips session refresh for is_staff users
    'SKIP_STAFF_USERS': False,

    # Skips session refresh for is_superuser users
    'SKIP_SUPERUSER_USERS': True,

    # Skips session refresh for static and media file requests
    'SKIP_STATIC_AND_MEDIA': True,

    # Skips session refresh for unauthenticated users
    'SKIP_UNAUTHENTICATED_USERS': True,
}
```

## Request features
After a successful session refresh, the middleware adds the following dictionary attribute to the `request` object:

- `request.django_session_refresh['refreshed']`: A boolean indicating whether the session was refreshed during the current request.
- `request.django_session_refresh['refreshed_at']`: A datetime object representing the timestamp when the session was last refreshed.
