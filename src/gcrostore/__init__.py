__version__ = "0.0.6"

# FastAPI
import fastapi

from . import config

app = fastapi.FastAPI(
    title="Crostore",
    version=__version__,
)


# Logging
import logging

console_handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
crostore_logger = logging.getLogger("crostore")
crostore_logger.addHandler(console_handler)


# Endpoints
api_version = "v" + __version__.split(".")[0]
from . import cancel, request
