"""
This module defines mappings for Withings health measurement types and attribution codes.

Attributes:
    measures (dict): Maps integer codes to human-readable descriptions of various health measurements
        recorded by Withings devices. The keys are integer identifiers, and the values are strings
        describing the measurement type and its unit (if applicable).

    attribution (dict): Maps integer codes to descriptions of how a measurement group was attributed
        to a user. The keys are integer identifiers, and the values are strings explaining the context
        or certainty of the measurement attribution.
"""

measures = {
    1: "Weight (kg)",
    4: "Height (meter)",
    5: "Fat Free Mass (kg)",
    6: "Fat Ratio (%)",
    8: "Fat Mass Weight (kg)",
    9: "Diastolic Blood Pressure (mmHg)",
    10: "Systolic Blood Pressure (mmHg)",
    11: "Heart Pulse (bpm)",
    12: "Temperature (celsius)",
    54: "SP02 (%)",
    71: "Body Temperature (celsius)",
    73: "Skin Temperature (celsius)",
    76: "Muscle Mass (kg)",
    77: "Hydration (kg)",
    88: "Bone Mass (kg)",
    91: "Pulse Wave Velocity (m/s)",
    123: "VO2 max",
    130: "Atrial fibrillation result",
    135: "QRS interval duration based on ECG signal",
    136: "PR interval duration based on ECG signal",
    137: "QT interval duration based on ECG signal",
    138: "Corrected QT interval duration based on ECG signal",
    139: "Atrial fibrillation result from PPG",
    155: "Vascular age",
    167: "Nerve Health Score Conductance 2 electrodes Feet",
    168: "Extracellular Water in kg",
    169: "Intracellular Water in kg",
    170: "Visceral Fat (without unity)",
    174: "Fat Mass for segments in mass unit",
    175: "Muscle Mass for segments",
    196: "Electrodermal activity feet",
    226: "Basal Metabolic Rate",
    229: "Electrochemical Skin Conductance",
}

attribution = {
    0: "The measuregroup has been captured by a device and is known to belong to this user (and is not ambiguous)",
    1: "The measuregroup has been captured by a device but may belong to other users as well as this one (it is ambiguous)",
    2: "The measuregroup has been entered manually for this particular user",
    4: "The measuregroup has been entered manually during user creation (and may not be accurate)",
    5: "Measure auto, it's only for the Blood Pressure Monitor. This device can make many measures and computed the best value",
    7: "Measure confirmed. You can get this value if the user confirmed a detected activity",
    8: "Same as attrib 'The measuregroup has been captured by a device and is known to belong to this user (and is not ambiguous)",
    15: "The measure has been performed in specific guided conditions. Apply to Nerve Health Score",
    17: "The measure has been performed in specific guided conditions. Apply to Nerve Health Score and Electrochemical Skin Conductance",
}
