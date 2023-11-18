__version__ = "0.1.0"

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
