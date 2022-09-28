__version__ = "0.0.1"

# FastAPI
import fastapi

from . import config

app = fastapi.FastAPI(
    title="Crostore",
    version=__version__,
)

# Middlewares
import os

import bugsnag
import bugsnag.asgi

bugsnag.configure(  # type: ignore[no-untyped-call]
    api_key=config.BUGSNAG_API_KEY,
    project_root=os.path.dirname(__file__),
)
app.add_middleware(bugsnag.asgi.BugsnagMiddleware)


# Logging
import logging

import bugsnag.handlers

logger = logging.getLogger(__name__)
bugsnag_handler = bugsnag.handlers.BugsnagHandler()  # type: ignore[no-untyped-call]
console_handler = logging.StreamHandler()
logger.addHandler(bugsnag_handler)
logger.addHandler(console_handler)

crostore_logger = logging.getLogger("crostore")
crostore_logger.addHandler(bugsnag_handler)
crostore_logger.addHandler(console_handler)


# Endpoints
api_version = "v" + __version__.split(".")[0]
from . import cancel, status
