"""A modern, typed, and robust Python client for the Microsoft Dynamics 365 Business Central OData API.

This package provides a convenient and feature-rich interface for interacting with
Business Central, including automatic retry mechanisms, pagination handling, and
pluggable authentication sessions.
"""

from ._client import Odyn
from ._exceptions import (
    InvalidBackoffFactorError,
    InvalidLoggerError,
    InvalidRetryError,
    InvalidSessionError,
    InvalidStatusForcelistError,
    InvalidTimeoutError,
    InvalidURLError,
)
from .sessions import BasicAuthSession, BearerAuthSession, OdynSession

__all__: list[str] = [
    "BasicAuthSession",
    "BearerAuthSession",
    "InvalidBackoffFactorError",
    "InvalidLoggerError",
    "InvalidRetryError",
    "InvalidSessionError",
    "InvalidStatusForcelistError",
    "InvalidTimeoutError",
    "InvalidURLError",
    "Odyn",
    "OdynSession",
]
