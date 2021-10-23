import functools


class ordered_partial(functools.partial):
    """
    Slightly modified version of functools.partial which changes the
    order in which the declared arguments and the new arguments are passed
    to the function
    """

    def __call__(*args, **keywords):
        # This is the old way (before 3.8) of using only positional arguments
        if not args:
            raise TypeError("descriptor '__call__' of partial needs an argument")
        self, *args = args
        # allow overwriting the declared keywords
        keywords = {**self.keywords, **keywords}
        return self.func(*args, *self.args, **keywords)
