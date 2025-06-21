"""A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData API.

This package provides a convenient and feature-rich interface for interacting with
Business Central, including automatic retry mechanisms, pagination handling, and
pluggable authentication sessions.
"""

from ._client import Odyn
from ._exceptions import (
    InvalidLoggerError,
    InvalidSessionError,
    InvalidTimeoutError,
    InvalidURLError,
)

__all__: list[str] = [
    "InvalidLoggerError",
    "InvalidSessionError",
    "InvalidTimeoutError",
    "InvalidURLError",
    "Odyn",
]
