class DomainError(Exception):
    """Base class for errors raised by business rules."""


class InvalidPetData(DomainError):
    pass
 

class InvalidUserData(DomainError):
    pass


class PetNotFound(DomainError):
    pass


class NotAllowed(DomainError):
    pass


class NotAuthenticated(DomainError):
    pass
