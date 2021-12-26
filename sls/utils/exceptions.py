"""Module for custom exception declarations"""

class AccountNotFound(Exception):
    pass

class InvalidRegionException(Exception):
    pass

class InvalidInputException(Exception):
    pass

class ResourceUnknownException(Exception):
    pass

class AuthorizationException(Exception):
    pass
