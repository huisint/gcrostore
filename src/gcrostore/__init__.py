__version__ = "0.1.0"

# FastAPI
import fastapi

from . import config as config

app = fastapi.FastAPI(
    title="Crostore",
    version=__version__,
)


# Endpoints
api_version = "v" + __version__.split(".")[0]
from . import cancel as cancel  # noqa: E402
from . import request as request  # noqa: E402
