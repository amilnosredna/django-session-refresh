# django-session-refresh
Django middleware to refresh user sessions periodically to prevent timeout during active use.

This middleware updates a timestamp in the session data at specified intervals,
effectively extending the session's lifetime as long as the user is active.

Configuration options (can be set in Django settings):
- SESSION_REFRESH_KEY: The session key to store the last refresh timestamp. Default is 'last_session_refresh'.
- SESSION_REFRESH_INTERVAL: The interval in seconds to refresh the session. Default is 86400 (24 hours).
- SESSION_REFRESH_SKIP_ADMIN_USERS: If True, skips session refresh for admin users. Default is True.
- SESSION_REFRESH_SKIP_STATIC_AND_MEDIA: If True, skips session refresh for static and media file requests. Default is True.
- SESSION_REFRESH_SKIP_UNAUTHENTICATED_USERS: If True, skips session refresh for unauthenticated users. Default is True.
