# Usage

Load configuration data from a JSON file, refresh tokens, save config data, get all available measures in freedom units and save to a JSON file.

```python
import json
from pathlib import Path
from pydantic.tools import parse_obj_as

from withingpy import WithingsAPIClient
from withingpy.models import WithingsConfig

# load config and create client
config_path = Path("withings_config.json")
config = parse_obj_as(WithingsConfig, json.loads(config_path.read_text()))
client = WithingsAPIClient(config)

# refresh token and save config
client.refresh_access_token()  
config_path.write_text(config.model_dump_json(indent=2))

# get all available results in pounds instead of kilograms and save to a JSON file
results = client.get_normalized_measures(last_update=0, pounds=True)
if results:
    Path("results.json").write_text(results.model_dump_json(indent=2))
```