class InferiusError(Exception):
    pass


class DependencyError(InferiusError):
    pass


class NotFoundError(InferiusError):
    pass


class InvalidChoiceError(InferiusError, ValueError):
    pass


class InvalidTypeError(InferiusError, TypeError):
    pass


class IOError(InferiusError, OSError):
    pass
