# coding: utf-8

""" Custom application-wide exception classes.

This module contains custom exception classes that can be used to wrap other
exception and allow for consistent error-handling across the application.
"""


class UnhandledError(Exception):
    def __init__(self, message, *args):
        super(UnhandledError, self).__init__(message, *args)


class ConfigFileNotFound(Exception):
    """ Exception raised when a JSON configuration file is missing."""
    def __init__(self, message, *args):
        super(ConfigFileNotFound, self).__init__(message, *args)


class ConfigFileInvalid(Exception):
    """ Exception raised when a JSON configuration file is invalid."""
    def __init__(self, message, *args):
        super(ConfigFileInvalid, self).__init__(message, *args)


class Auth0JwksRetrievalError(Exception):
    """ Exception raised when the Auth0 JSON Web Key Set could not be
        retrieved.
    """
    def __init__(self, message, *args):
        super(Auth0JwksRetrievalError, self).__init__(message, *args)


class Auth0TokenRetrievalError(Exception):
    """ Exception raised when the Auth0 JWT token could not be retrieved."""

    def __init__(self, message, *args):
        super(Auth0TokenRetrievalError, self).__init__(message, *args)
