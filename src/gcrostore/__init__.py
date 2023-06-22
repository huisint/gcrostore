__version__ = "0.0.9"

# FastAPI
import fastapi

from . import config

app = fastapi.FastAPI(
    title="Crostore",
    version=__version__,
)


# Endpoints
api_version = "v" + __version__.split(".")[0]
from . import cancel, request
