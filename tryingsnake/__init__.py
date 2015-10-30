# -*- coding: utf-8 -*-


class Try_(object):
    @staticmethod
    def _identity_if_try_or_raise(v, msg="Invalid return type for f: {0}"):
        if not isinstance(v, Try_):
            raise TypeError(msg.format(type(v)))
        return v

    @staticmethod
    def _raise_if_not_exception(e, msg="Invalid type for Failure: {0}"):
        if not isinstance(e, Exception):
            raise TypeError(msg.format(type(e)))
        return True

    def __init__(self, _):
        raise NotImplementedError("Use Try function or Success/Failure instead.")  # pragma: no cover

    def __repr__(self):
        return self._fmt.format(repr(self._v))

    def get(self):
        """If this is Success get wrapped value otherwise
        throw stored exception

        :return: stored value

        >>> Success(1).get()
        1
        >>> Failure(Exception("e")).get()
        Traceback (most recent call last):
            ...
        Exception: e
        """
        raise NotImplementedError  # pragma: no cover

    def getOrElse(self, default):
        """If this is a Success get stored value otherwise
        return default

        :param default: value to return if this is a Failure
        :return:

        >>> Success(1).getOrElse(0)
        1
        >>> Failure(Exception("e")).getOrElse(0)
        0
        """
        raise NotImplementedError  # pragma: no cover

    def orElse(self, default):
        """If this is a Success return self otherwise
        default

        :param default: Try_
        :return:

        >>> Success(1).orElse(Success(0))
        Success(1)
        >>> Failure(Exception("e")).orElse(Success(0))
        Success(0)
        """
        raise NotImplementedError  # pragma: no cover

    def map(self, f):
        """Apply function to the value.

        :param f: function to be applied
        :return: self if this is a Failure otherwise Try(f, self.get)

        >>> inc = lambda x: x + 1
        >>> def f(e): raise Exception("e")
        >>> Success(1).map(inc)
        Success(2)
        >>> Failure(Exception("e")).map(inc)
        Failure(Exception('e',))
        >>> Success("1").map(f)
        Failure(Exception('e',))
        """
        raise NotImplementedError   # pragma: no cover

    def flatMap(self, f):
        """ Apply function  returning Try_ to the value.

        :param f: function to be applied.
        :return: self if this is a Failure otherwise f applied to self.get

        >>> from operator import add
        >>> Success(1).flatMap(lambda x: Try(add, x, 1))
        Success(2)
        >>> Failure(Exception("e")).flatMap(lambda x: Try(add, x, 1))
        Failure(Exception('e',))
        >>> Success(1).flatMap(lambda x: Try(add, x, "0")) # doctest:+ELLIPSIS
        Failure(TypeError(...))
        """
        raise NotImplementedError  # pragma: no cover

    def filter(self, f, exception_cls=Exception, msg=None):
        """Convert this to Failure if f(self.get()) evaluates to False

        :param f: function to be applied
        :param exception_cls: optional exception class to return
        :param msg: optional message
        :return: self if f evaluates to True otherwise Failure

        >>> Success(1).filter(lambda x: x > 0)
        Success(1)
        >>> Success(1).filter(lambda x: x < 0, msg="Greater than zero")
        Failure(Exception('Greater than zero',))
        >>> Failure(Exception("e")).filter(lambda x: x)
        Failure(Exception('e',))
        """
        raise NotImplementedError  # pragma: no cover

    def recover(self, f):
        """If this is a Failure apply f to value otherwise

        :param f: function to be applied
        :return: Either Success of Failure

        >>> def f(e): raise Exception("e")
        >>> Success(1).recover(lambda e: 0)
        Success(1)
        >>> Failure(Exception("e")).recover(lambda e: 0)
        Success(0)
        >>> Failure(Exception("e")).recover(f)
        Failure(Exception('e',))
        """
        raise NotImplementedError  # pragma: no cover

    def recoverWith(self, f):
        """If this is a Failure apply f to self otherwise
        return this

        :param f: function to be applied
        :return: Either Success of Failure

        >>> Success(1).recoverWith(lambda t: Try(lambda: 0))
        Success(1)
        >>> Failure(Exception("e")).recoverWith(lambda t: Try(lambda: 0))
        Success(0)
        """
        raise NotImplementedError  # pragma: no cover

    def failed(self):
        """If this is a failure complete wrapped exception
        otherwise throw TypeError

        :return: None

        >>> Success(1).failed()
        Traceback (most recent call last):
            ...
        TypeError: Cannot fail Success
        >>> Failure(Exception("e")).failed()
        Traceback (most recent call last):
            ...
        Exception: e
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def isFailure(self):
        """Check if this is a Failure.

        >>> Success(1).isFailure
        False
        >>> Failure(Exception()).isFailure
        True
        """
        return not self._isSuccess

    @property
    def isSuccess(self):
        """Check if this is a Success.

        >>> Success(1).isSuccess
        True
        >>> Failure(Exception()).isSuccess
        False
        """
        return self._isSuccess


class Success(Try_):
    """Represents a successful computation"""

    def __init__(self, v):
        self._v = v
        self._isSuccess = True
        self._fmt = "Success({0})"

    def get(self): return self._v

    def getOrElse(self, default): return self.get()

    def orElse(self, defualt): return self

    def map(self, f):
        return Try(f, self._v)

    def flatMap(self, f):
        v = Try(f, self._v)
        return Try_._identity_if_try_or_raise(v if v.isFailure else v.get())

    def filter(self, f, exception_cls=Exception, msg=None):
        return (self if f(self.get())
                else Failure(exception_cls(msg if msg else repr(f))))

    def recover(self, f):
        return self

    def recoverWith(self, f):
        return self

    def failed(self):
        raise TypeError("Cannot fail Success")


class Failure(Try_):
    """Represents a unsuccessful computation"""

    def __init__(self, e):
        Try_._raise_if_not_exception(e)
        self._v = e
        self._isSuccess = False
        self._fmt = "Failure({0})"

    def get(self): raise self._v

    def getOrElse(self, default):
        return default

    def orElse(self, default):
        return Try_._identity_if_try_or_raise(default)

    def map(self, f):
        return self

    def flatMap(self, f):
        return self

    def filter(self, f, exception_cls=Exception, msg=None):
        return self

    def recover(self, f):
        return Try(f, self._v)

    def recoverWith(self, f):
        v = Try(f, self._v)
        return Try_._identity_if_try_or_raise(v if v.isFailure else v.get())

    def failed(self):
        return self.get()


def Try(f, *args, **kwargs):
    """Calls f with provided arguments and wraps the result
    using either Success or Failure.

    :param f: Callable which should be evaluated
    :param args: args which should be passed to f
    :param kwargs: kwargs which should be passed to f
    :return: Either success or Failure

    >>> from operator import add, truediv
    >>> Try(truediv, 1, 0) # doctest:+ELLIPSIS
    Failure(ZeroDivisionError(...))
    >>> Try(add, 1, 2)
    Success(3)
    """
    try:
        return Success(f(*args, **kwargs))
    except Exception as e:
        return Failure(e)
