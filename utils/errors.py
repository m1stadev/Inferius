class InferiusError(Exception):
    pass

class NotFoundError(InferiusError):
    pass

class InvalidChoiceError(ValueError):
    pass

class InvalidTypeError(TypeError):
    pass