import hashlib
import hmac
import logging
import time
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests

from withingpy.models import (
    WithingsBoneMass,
    WithingsConfig,
    WithingsFatMass,
    WithingsLeanMass,
    WithingsMeasurements,
    WithingsMuscleMass,
    WithingsVisceralFat,
    WithingsWaterMass,
    WithingsWeight,
)
from withingpy.values import attribution


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""

    pass


class WithingsAPIClient:
    def __init__(self, config: WithingsConfig):
        """Initializes the WithingsApiClient with the provided configuration.

        Args:
            config (WithingsConfig): The configuration object containing Withings API credentials and settings.
        """
        self.config = config

    def _headers(self) -> dict[str, str]:
        """Generate HTTP headers for API requests.

        Returns:
            dict[str, str]: A dictionary containing the HTTP headers, including the
            Authorization header with a Bearer token if an access token is available,
            and the Content-Type header set to 'application/x-www-form-urlencoded'.
        """
        return {
            "Authorization": f"Bearer {self.config.access_token}" if self.config.access_token else "",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _generate_signature(self, action: str) -> str:
        """Generates a HMAC-SHA256 signature for the given action using client credentials.

        The signature is created by hashing a comma-delimited string of sorted parameter values,
        which include the action, client ID, current timestamp, and a nonce. The client secret is
        used as the HMAC key.

        Args:
            action (str): The action for which the signature is being generated.

        Returns:
            str: The generated hexadecimal HMAC-SHA256 signature.
        """
        params = {
            "action": action,
            "client_id": self.config.client_id,
            "timestamp": int(time.time()),
            "nonce": self.get_nonce(),
        }
        sorted_values = ",".join(str(value) for value in params.values())
        hmac_obj = hmac.new(self.config.client_secret.encode(), sorted_values.encode(), hashlib.sha256)
        return hmac_obj.hexdigest()

    def get_nonce(self) -> str:
        """Requests a nonce value from the Withings API for use in request signing.

        Sends a POST request to the /v2/signature endpoint with the required authentication
        parameters, including client ID, timestamp, and a generated signature. Parses the
        response to extract and return the nonce value.

        Returns:
            str: The nonce value retrieved from the API response.

        Raises:
            ValueError: If the nonce is not found in the API response.
            requests.HTTPError: If the HTTP request fails.
        """
        url = f"{self.config.base_url}/v2/signature"
        data = {
            "action": "getnonce",
            "client_id": self.config.client_id,
            "timestamp": int(time.time()),
            "signature": self._generate_signature("getnonce"),
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if value := resp.json().get("body", {}).get("nonce"):
            return value
        else:
            raise ValueError("Nonce not found in response")

    def get_access_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchanges an authorization code for an access token from the Withings API.

        Args:
            code (str): The authorization code received from the OAuth2 authorization step.
            redirect_uri (str): The redirect URI used in the OAuth2 flow.

        Returns:
            dict[str, Any]: The JSON response from the Withings API containing the access token and related information.

        Raises:
            ValueError: If the API response status code is not 200.
            requests.HTTPError: If the HTTP request fails.
        """
        url = f"{self.config.base_url}/v2/oauth2"
        data = {
            "action": "requesttoken",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise ValueError(f"Failed to get access token: {resp.text}")
        return resp.json()

    def refresh_access_token(self) -> None:
        """Refreshes the OAuth2 access token using the stored refresh token.

        Sends a POST request to the Withings OAuth2 endpoint to obtain a new access token and refresh token.
        Updates the configuration with the new tokens upon success.

        Raises:
            ValueError: If the HTTP response status code is not 200.
            AuthenticationError: If the API response indicates authentication failure.
        """
        url = f"{self.config.base_url}/v2/oauth2"
        data = {
            "action": "requesttoken",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.config.refresh_token,
        }
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise ValueError(f"Failed to refresh access token: {resp.text}")
        else:
            if resp.json().get("status") != 0:
                raise AuthenticationError(f"Authentication failed: {resp.json().get('error', 'Unknown error')}")
            else:
                self.config.access_token = resp.json().get("body", {}).get("access_token")
                self.config.refresh_token = resp.json().get("body", {}).get("refresh_token")

    def get_raw_measures(self, last_update: int = 0) -> dict[str, Any]:
        """Fetches raw measurement data from the Withings API.

        Attempts to retrieve measurement data using a POST request to the Withings API endpoint.
        Implements up to 3 retries with exponential backoff in case of authorization errors (status 401).
        If an authorization error occurs, attempts to refresh the access token and retry the request.
        Raises a RuntimeError if the request fails after the maximum number of attempts or if an unexpected error occurs.

        Args:
            last_update (int, optional): Unix timestamp to fetch measurements updated since this time. Defaults to 0.

        Returns:
            dict[str, Any]: The JSON response from the Withings API containing measurement data.

        Raises:
            RuntimeError: If the request fails after 3 attempts or if an unexpected error occurs.
        """
        url = "https://scalews.withings.com/measure"
        data = {"action": "getmeas", "lastupdate": last_update}

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

    def _compute_value(self, value: float, unit: int, pounds: bool) -> float:
        """Computes the measurement value based on the provided value, unit, and desired output unit.

        Args:
            value (float): The raw measurement value.
            unit (int): The power of ten exponent to scale the value.
            pounds (bool): If True, converts the result to pounds; otherwise, returns the value in kilograms.

        Returns:
            float: The computed measurement value, scaled and optionally converted to pounds.
        """
        if pounds:
            return value * pow(10, unit) * 2.20462
        else:
            return value * pow(10, unit)

    def get_normalized_measures(self, last_update: int = 0, pounds: bool = False) -> WithingsMeasurements:
        """Retrieve and normalize body composition measures from the Withings API.

        This method fetches raw measurement data, processes it, and returns a structured
        `WithingsMeasurements` object containing lists of various body composition metrics,
        such as weight, fat mass, muscle mass, water mass, visceral fat, bone mass, and lean mass.
        Each measurement is normalized to either kilograms or pounds, depending on the `pounds` flag.

        Args:
            last_update (int, optional): Unix timestamp to filter measurements updated after this time.
                Defaults to 0, which retrieves all available measurements.
            pounds (bool, optional): If True, converts weight-related measurements to pounds (lb).
                If False, measurements are in kilograms (kg). Defaults to False.

        Returns:
            WithingsMeasurements: An object containing lists of normalized measurement data for each
                supported body composition metric.

        Notes:
            - The method logs a warning for unsupported measurement types.
            - Timezone information is extracted from the API response and used to localize timestamps.
            - Each measurement includes attribution, timestamps (taken, created, modified), device ID,
              value, and unit of measurement (where applicable).
        """
        raw_measures = self.get_raw_measures(last_update=last_update)
        tz = raw_measures.get("body", {}).get("timezone")

        measurements = WithingsMeasurements(
            weight=[],
            fat_mass=[],
            muscle_mass=[],
            water_mass=[],
            visceral_fat=[],
            bone_mass=[],
            lean_mass=[],
        )
        for result in raw_measures.get("body", {}).get("measuregrps", []):
            dt_date = datetime.fromtimestamp(result["date"], tz=ZoneInfo(tz))
            dt_created = datetime.fromtimestamp(result["created"], tz=ZoneInfo(tz))
            dt_modified = datetime.fromtimestamp(result["modified"], tz=ZoneInfo(tz))
            for measure in result.get("measures", []):
                if measure["type"] == 1:
                    measurements.weight.append(
                        WithingsWeight(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                elif measure["type"] == 8:
                    # Fat Mass Weight
                    measurements.fat_mass.append(
                        WithingsFatMass(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                elif measure["type"] == 76:
                    # Muscle Mass
                    measurements.muscle_mass.append(
                        WithingsMuscleMass(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                elif measure["type"] == 77:
                    # Hydration (Water Mass)
                    measurements.water_mass.append(
                        WithingsWaterMass(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                elif measure["type"] == 170:
                    # Visceral Fat
                    measurements.visceral_fat.append(
                        WithingsVisceralFat(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=measure["value"] * pow(10, measure.get("unit")),
                        )
                    )
                elif measure["type"] == 88:
                    # Bone Mass
                    measurements.bone_mass.append(
                        WithingsBoneMass(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                elif measure["type"] == 5:
                    # Fat Free Mass
                    measurements.lean_mass.append(
                        WithingsLeanMass(
                            attribution=attribution.get(result.get("attrib"), "Unknown"),
                            taken=dt_date,
                            created=dt_created,
                            modified=dt_modified,
                            deviceid=result.get("deviceid"),
                            value=self._compute_value(value=measure["value"], unit=measure.get("unit"), pounds=pounds),
                            uom="lb" if pounds else "kg",
                        )
                    )
                else:
                    logger.warning(f"Unsupported measure type {measure['type']} with value {measure['value']} and unit {measure.get('unit')}")

        return measurements
