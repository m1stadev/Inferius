class InferiusError(Exception):
    pass


class DependencyError(InferiusError):
    pass


class NotFoundError(InferiusError):
    pass


class DeviceError(InferiusError):
    pass


class CorruptError(InferiusError):
    pass


class BadIPSWError(CorruptError):
    pass


class RestoreError(InferiusError):
    pass
