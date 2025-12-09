import logging

default_logger = logging.getLogger("django.contrib.auth")


class RequestFormatter(logging.Formatter):
    """
    Extend logging to include request info (method, path, user)
    when available.
    """

    def format(self, record):
        record.method = getattr(record, "method", "-")
        record.path = getattr(record, "path", "-")
        record.user = getattr(record, "user", "-")
        return super().format(record)


class LoggingContextMiddleware:
    """
    Attach request-specific fields to log records.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    # def __call__(self, request):
    #     # Store values that logging can pick up
    #     logging.LoggerAdapter(
    #         logger,
    #         {
    #             "method": request.method,
    #             "path": request.path,
    #             "user": request.user.username if request.user.is_authenticated else "anonymous"
    #         }
    #     )

    #     return self.get_response(request)


# Add the middleware to your settings:
# MIDDLEWARE = [
#     # ...
#     "myapp.middleware.LoggingContextMiddleware",
# ]

# Configure Django LOGGING in settings.py
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,

#     "formatters": {
#         "verbose_request": {
#             "()": "myapp.logging.RequestFormatter",
#             "format": (
#                 "[{asctime}] "
#                 "{levelname} "
#                 "user={user} "
#                 "method={method} "
#                 "path={path} "
#                 "module={module} "
#                 "message={message}"
#             ),
#             "style": "{",
#         },
#     },

#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "verbose_request",
#         },
#         "file": {
#             "class": "logging.FileHandler",
#             "formatter": "verbose_request",
#             "filename": "logs/app.log",
#         },
#     },

#     "loggers": {
#         "django.request": {
#             "handlers": ["console", "file"],
#             "level": "INFO",
#             "propagate": True,
#         },
#         "myapp": {  # your app’s logs
#             "handlers": ["console", "file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# }
