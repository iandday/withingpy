from importlib.metadata import version as get_version

from .models import WithingsConfig
from .withings_api_client import WithingsAPIClient


__version__ = get_version("withingpy")
