# Usage

```python
import json
from pathlib import Path

from withingpy import WithingsAPIClient
from withingpy.models import WithingsConfig

# load config and create client
config_path = Path("withings_config.json")
config = WithingsConfig(**json.loads(config_path.read_text()))
client = WithingsAPIClient(config)

# refresh token and save config
client.refresh_access_token()  
config_path.write_text(config.model_dump_json(indent=2))

# get all available results in pounds instead of kilograms and save to a JSON file
results = client.get_normalized_measures(last_update=0, pounds=True)
if results:
    Path("results.json").write_text(results.model_dump_json(indent=2))
```