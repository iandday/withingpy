# Usage

```python
from withings_api import WithingsAPI, WithingsConfig

config = WithingsConfig(
    base_url="https://wbsapi.withings.net",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
api = WithingsAPI(config)
# Example: Get nonce
nonce = api.get_nonce()
print(nonce)
```