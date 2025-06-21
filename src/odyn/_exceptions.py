class OdynError(Exception):
    """Base exception for all Odyn exceptions."""


class InvalidURLError(OdynError):
    """Exception raised when an invalid URL is provided."""


class InvalidSessionError(OdynError):
    """Exception raised when an invalid session is provided."""


class InvalidLoggerError(OdynError):
    """Exception raised when an invalid logger is provided."""


class InvalidTimeoutError(OdynError):
    """Exception raised when an invalid timeout is provided."""


class InvalidRetryError(OdynError):
    """Exception raised when an invalid retry is provided."""


class InvalidBackoffFactorError(OdynError):
    """Exception raised when an invalid backoff factor is provided."""


class InvalidStatusForcelistError(OdynError):
    """Exception raised when an invalid status forcelist is provided."""
