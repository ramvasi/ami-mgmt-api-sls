"""Module for custom exception declarations"""

class GQLException(Exception):
    pass

class GQLAccountNotFound(Exception):
    pass

class GQLMissingParameter(Exception):
    pass
