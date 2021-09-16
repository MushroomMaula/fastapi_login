import functools


class ordered_partial(functools.partial):
    """
    Slightly modified version of functools.partial which changes the
    order in which the declared arguments and the new arguments are passed
    to the function
    """

    def __call__(self, /, *args, **keywords):
        # allow overwriting the declared keywords
        keywords = {**self.keywords, **keywords}
        return self.func(*args, *self.args, **keywords)
