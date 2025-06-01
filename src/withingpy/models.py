from datetime import datetime

from pydantic import BaseModel


class WithingsConfig(BaseModel):
    base_url: str
    client_id: str
    client_secret: str
    access_token: str | None = None
    refresh_token: str | None = None


class BaseMeasurement(BaseModel):
    attribution: str | None = None
    taken: datetime
    created: datetime
    modified: datetime
    deviceid: str | None = None
    value: float | None = None


class WithingsWeight(BaseMeasurement):
    uom: str = "kg"


class WithingsFatMass(BaseMeasurement):
    uom: str = "kg"


class WithingsMuscleMass(BaseMeasurement):
    uom: str = "kg"


class WithingsWaterMass(BaseMeasurement):
    uom: str = "kg"


class WithingsVisceralFat(BaseMeasurement):
    uom: str | None = None


class WithingsBoneMass(BaseMeasurement):
    uom: str = "kg"


class WithingsLeanMass(BaseMeasurement):
    uom: str = "kg"


class WithingsMeasurements(BaseModel):
    """Container for various Withings measurements."""

    weight: list[WithingsWeight] = []
    fat_mass: list[WithingsFatMass] = []
    muscle_mass: list[WithingsMuscleMass] = []
    water_mass: list[WithingsWaterMass] = []
    visceral_fat: list[WithingsVisceralFat] = []
    bone_mass: list[WithingsBoneMass] = []
    lean_mass: list[WithingsLeanMass] = []
