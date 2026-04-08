# django-session-refresh
A simple Django middleware to refresh user sessions periodically (24h by default) to prevent timeout during user activity.

This middleware updates a timestamp in the session data at specified intervals,
effectively extending the session's lifetime as long as the user is active.

## Installation
1. Run `pip install django-session-refresh`
2. Add `session_refresh.middleware.SessionRefreshMiddleware` settings.py ass bellow

```python
MIDDLEWARE = [
    ...
    'django.contrib.sessions.middleware.SessionMiddleware',  # Django default SessionMiddleware
    'session_refresh.middleware.SessionRefreshMiddleware',   # django-session-refresh
    ...
]
```

## Configuration (optional)
The settings bellow are optional and if not defined in settings.py the default values will be used.

```python
# The interval in seconds to refresh the session
SESSION_REFRESH_INTERVAL = 86400  # 24 hours
```
```python
# The name of the session key to store the last refresh timestamp
SESSION_REFRESH_KEY = 'last_session_refresh'
```
```python
# Skips session refresh for is_staff users
SESSION_REFRESH_SKIP_STAFF_USERS = False
```
```python
# Skips session refresh for is_superuser users
SESSION_REFRESH_SKIP_SUPERUSER_USERS = True
```
```python
# Skips session refresh for static and media file requests
SESSION_REFRESH_SKIP_STATIC_AND_MEDIA = True
```
```python
# Skips session refresh for unauthenticated users
SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS = True
```
