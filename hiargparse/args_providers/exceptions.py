class ArgumentError(ValueError):
    """An error from hiargparse.Arg construction."""
    pass


class ConflictWarning(UserWarning):
    """An warning that tells conflicts of some arguments."""
    pass


class PropagationError(Exception):
    """An error from hiargparse argument propagation."""
    pass


class ConflictError(ValueError):
    """An error from hiargparse parameter conflicttion"""
    pass
