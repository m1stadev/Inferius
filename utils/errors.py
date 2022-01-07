class InferiusError(Exception):
    pass

class DependencyError(InferiusError):
    pass

class NotFoundError(InferiusError):
    pass

class InvalidChoiceError(ValueError):
    pass

class InvalidTypeError(TypeError):
    pass