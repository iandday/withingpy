import hashlib
import hmac
import logging
import time
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


from withingpy.models import WithingsConfig

class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass

logger = logging.getLogger(__name__)

class WithingsAPIClient:
    def __init__(self, config: WithingsConfig):
        self.config = config

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}" if self.config.access_token else "",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _timestamp(self) -> int:
        import time
        return int(time.time())

    def _generate_signature(self, action: str) -> str:
        params = {
        'action': action,
        'client_id': self.config.client_id,
        'timestamp': self._timestamp(),
        'nonce': self.get_nonce(),
        }

        # hash content is comma delimited sorted values
        sorted_values = ','.join(str(value) for value in params.values()) 
        hmac_obj = hmac.new(self.config.client_secret.encode(), sorted_values.encode(), hashlib.sha256) 
        return hmac_obj.hexdigest()
        
    
    def get_nonce(self) -> str:
        url = f"{self.config.base_url}/v2/signature"
        data = {
            "action": "getnonce",
            "client_id": self.config.client_id,
            "timestamp": self._timestamp(),
            "signature": self._generate_signature("getnonce")
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if value := resp.json().get("body",{}).get("nonce"):
            return value
        else:
            raise ValueError("Nonce not found in response")

    def get_access_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = f"{self.config.base_url}/v2/oauth2"
        data = {
            "action": "requesttoken",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise ValueError(f"Failed to get access token: {resp.text}")
        return resp.json()

    def refresh_access_token(self) -> None:
        url = f"{self.config.base_url}/v2/oauth2"
        data = {
            "action": "requesttoken",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.config.refresh_token
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise ValueError(f"Failed to refresh access token: {resp.text}")
        else:
            self.config.access_token = resp.json().get("body", {}).get("access_token")
            self.config.refresh_token = resp.json().get("body", {}).get("refresh_token")

    def get_measures(self, lastupdate: int = 0) -> Dict[str, Any]:

        url = "https://scalews.withings.com/measure"
        data = {
            "action": "getmeas",
            "lastupdate": lastupdate
        }

        attempts = 0
        max_attempts = 3
        backoff = 1

        while attempts < max_attempts:
            resp = requests.post(url, data=data, headers=self._headers())
            resp.raise_for_status()
            if resp.status_code == 200:
                real_status = resp.json().get("status")
                if real_status == 401:
                    logger.error("Unauthorized request, trying to refresh access token.")
                    # Try to refresh token and retry
                    self.refresh_access_token()
                    attempts += 1
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                elif real_status == 0:
                    return resp.json()
                else:
                    logger.error(f"Error fetching measures: {resp.json().get('error', 'Unknown error')}")
                    raise RuntimeError(f"Error fetching measures: {resp.json().get('error', 'Unknown error')}")
            else:
                logger.error(f"Unexpected status code: {resp.status_code}, response: {resp.text}")
                raise RuntimeError(f"Unexpected status code: {resp.status_code}")
        raise RuntimeError("Failed to fetch measures after 3 attempts (with exponential backoff).")

    def get_activity(self, lastupdate: int) -> Dict[str, Any]:
        url = f"{self.config.base_url}/v2/measure"
        data = {
            "action": "getactivity",
            "lastupdate": lastupdate,
            "data_fields": "steps,distance,elevation,soft,moderate,intense,active,calories,totalcalories,hr_average,hr_min,hr_max,hr_zone_0,hr_zone_1,hr_zone_2,hr_zone_3"
        }
        resp = requests.post(url, data=data, headers=self._headers())
        return resp.json()

    def get_sleep_summary(self, lastupdate: int) -> Dict[str, Any]:
        url = f"{self.config.base_url}/v2/sleep"
        data = {
            "action": "getsummary",
            "lastupdate": lastupdate,
            "data_fields": "nb_rem_episodes,sleep_efficiency,sleep_latency,total_sleep_time,total_timeinbed,wakeup_latency,waso,apnea_hypopnea_index,breathing_disturbances_intensity,asleepduration,deepsleepduration,durationtosleep,durationtowakeup,hr_average,hr_max,hr_min,lightsleepduration,night_events,out_of_bed_count,remsleepduration,rr_average,rr_max,rr_min,sleep_score,snoring,snoringepisodecount,wakeupcount,wakeupduration"
        }
        resp = requests.post(url, data=data, headers=self._headers())
        return resp.json()

    # Add more methods for other endpoints as needed...



# Example usage:
# config = WithingsConfig(base_url="https://wbsapi.withings.net", client_id="...", client_secret="...")
# api = WithingsAPI(config)
# nonce = api.get_nonce()