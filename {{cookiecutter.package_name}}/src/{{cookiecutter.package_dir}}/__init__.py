{%- if cookiecutter.use_sentry == "y" -%}
import sentry_sdk

from {{ cookiecutter.package_dir }}.settings import SENTRY_DSN

{% endif -%}
__version__ = "0.1.0"

{%- if cookiecutter.use_sentry == "y" %}

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )
{%- endif %}
