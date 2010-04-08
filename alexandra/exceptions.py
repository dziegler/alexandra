class AlexandraException(Exception):
    """Base exception class for alexandra"""
    pass
    
class ConfigurationError(AlexandraException):
    """Raised when alexandra is not propertly configured"""
    pass
    