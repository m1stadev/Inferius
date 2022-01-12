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


class InferiusIOError(InferiusError, OSError):
    pass


class DeviceError(InferiusError):
    pass


class CorruptError(InferiusError):
    pass
