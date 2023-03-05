
from typing import Dict

from flask import request
import structlog

from utils import metadata


def field_name_modifier(
    logger: structlog._loggers.PrintLogger, log_method: str, event_dict: Dict
) -> Dict:
    """Changes the keys for some of the fields,
    to match Cloud Logging's expectations
    https://cloud.google.com/run/docs/logging#special-fields
    """
    # structlog example adapted from
    # https://github.com/ymotongpoo/cloud-logging-configurations/blob/master/python/structlog/main.py

    event_dict["severity"] = event_dict["level"]
    del event_dict["level"]

    if "event" in event_dict:
        event_dict["message"] = event_dict["event"]
        del event_dict["event"]
    return event_dict


def trace_modifier(
    logger: structlog._loggers.PrintLogger, log_method: str, event_dict: Dict
) -> Dict:
    """Adds Tracing correlation
    https://cloud.google.com/run/docs/logging#correlate-logs
    """
    # Only attempt to get the context if in a request
    if request:

        trace_header = request.headers.get("X-Cloud-Trace-Context")
        # Only append the trace if it exists in the request
        if trace_header:
            trace = trace_header.split("/")
            project = metadata.get_project_id()
            event_dict[
                "logging.googleapis.com/trace"
            ] = f"projects/{project}/traces/{trace[0]}"
    return event_dict


def getJSONLogger() -> structlog._config.BoundLoggerLazyProxy:
    """Create a JSON logger using the field name and trace modifiers created above"""
    # extend using https://www.structlog.org/en/stable/processors.html
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            field_name_modifier,
            trace_modifier,
            structlog.processors.TimeStamper("iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    return structlog.get_logger()


logger = getJSONLogger()


def flush() -> None:
    # Setting PYTHONUNBUFFERED in Dockerfile/Buildpack ensured no buffering

    # https://docs.python.org/3/library/logging.html#logging.shutdown
    # When the logging module is imported, it registers this
    # function as an exit handler (see atexit), so normally
    # there’s no need to do that manually.
    pass
