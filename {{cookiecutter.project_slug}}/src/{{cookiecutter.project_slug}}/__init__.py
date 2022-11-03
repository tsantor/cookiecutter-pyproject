import sentry_sdk

from {{ cookiecutter.project_slug }}.settings import SENTRY_DSN

__version__ = "0.1.0"

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )
