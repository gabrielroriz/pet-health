class DomainError(Exception):
    """Base class for errors raised by business rules."""


# Input that breaks a business rule: HTTP 422.
class InvalidPetData(DomainError):
    pass


class InvalidUserData(DomainError):
    pass


class InvalidAppointmentData(DomainError):
    pass


# Something referenced doesn't exist: HTTP 404.
class PetNotFound(DomainError):
    pass


class AppointmentNotFound(DomainError):
    pass


class HospitalNotFound(DomainError):
    pass


class VeterinarianNotFound(DomainError):
    pass


# The request conflicts with what is already booked: HTTP 409.
class DoubleBooking(DomainError):
    """The appointment overlaps another scheduled one for the same veterinarian or pet."""


class AgendaChanged(DomainError):
    """Another booking changed the veterinarian's agenda since it was read (optimistic lock)."""


class AppointmentAlreadyCancelled(DomainError):
    pass


# Acting on another user's data: HTTP 403.
class NotAllowed(DomainError):
    pass


# Missing or invalid token: HTTP 401.
class NotAuthenticated(DomainError):
    pass
