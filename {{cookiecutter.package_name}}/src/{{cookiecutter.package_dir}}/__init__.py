{%- if cookiecutter.use_sentry == "y" -%}
import sentry_sdk

from {{ cookiecutter.package_dir }}.settings import sentry_config

{% endif -%}
__version__ = "0.1.0"

{%- if cookiecutter.use_sentry == "y" %}
if sentry_config.dsn:
    sentry_sdk.init(
        dsn=sentry_config.dsn,
        environment=sentry_config.env,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )
{%- endif %}
