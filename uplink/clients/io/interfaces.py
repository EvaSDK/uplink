# Standard library imports
from abc import ABCMeta, abstractmethod, abstractproperty

# Local imports
from uplink import compat


class IllegalRequestStateTransition(RuntimeError):
    """An improper request state transition was attempted."""

    def __init__(self, state, transition):
        self._state = state
        self._transition = transition

    def __str__(self):
        return (
            "Illegal transition [%s] from request state [%s]: this is "
            "possibly due to a badly designed RequestTemplate."
            % (self._transition, self._state)
        )


class InvokeCallback(object):
    """
    Callbacks to continue the running request execution after invoking
    a function using the underlying I/O model.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_success(self, result):
        """
        Handles a successful invocation.

        Args:
            result: The invocation's return value.
        """

    @abstractmethod
    def on_failure(self, exc_type, exc_val, exc_tb):
        """
        Handles a failed invocation.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """


class SleepCallback(object):
    """
    Callbacks to continue the running request execution after an
    intended pause.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_success(self):
        """Handles a successful pause."""

    @abstractmethod
    def on_failure(self, exc_type, exc_val, exc_tb):
        """
        Handles a failed pause.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """


class Executable(compat.abc.Iterator):
    """An abstraction for iterating over the execution of a request."""
    __metaclass__ = ABCMeta

    def __next__(self):
        return self.execute()

    next = __next__

    @abstractmethod
    def execute(self):
        """Continues the request's execution."""


class RequestExecution(Executable):
    """A state machine representing the execution lifecycle of a request."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def state(self):
        """The current state of the request."""

    @abstractmethod
    def send(self, request, callback):
        """
        Sends the given request.

        Args:
            request: The intended request data to be sent.
            callback (InvokeCallback): A callback that resumes execution
                after the request is sent.
        """

    @abstractmethod
    def sleep(self, duration, callback):
        """
        Pauses the execution for the allotted duration.

        Args:
            duration: The number of seconds to delay execution.
            callback (:obj:`SleepCallback`): A callback that resumes
                execution after the delay.
        """

    @abstractmethod
    def finish(self, response):
        """
        Completes the execution.

        Args:
            response: The object to return to the execution's invoker.
        """

    @abstractmethod
    def fail(self, exc_type, exc_val, exc_tb):
        """
        Fails the execution with a specific error.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """

    @abstractmethod
    def execute(self):
        """Performs the next sequence of steps in the execution."""

    @abstractmethod
    def before_request(self, request):
        """Handles transitioning the execution before the request is sent."""

    @abstractmethod
    def after_response(self, request, response):
        """Handles transitioning the execution after a successful request."""

    @abstractmethod
    def after_exception(self, request, exc_type, exc_val, exc_tb):
        """Handles transitioning the execution after a failed request."""

    @abstractmethod
    def start(self, request):
        """Starts the request's execution."""


class RequestState(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def request(self):
        ...

    def send(self, request):
        raise IllegalRequestStateTransition(self, "send")

    def prepare(self, request):
        raise IllegalRequestStateTransition(self, "prepare")

    def sleep(self, duration):
        raise IllegalRequestStateTransition(self, "sleep")

    def finish(self, response):
        raise IllegalRequestStateTransition(self, "finish")

    def fail(self, exc_type, exc_val, exc_tb):
        raise IllegalRequestStateTransition(self, "fail")

    @abstractmethod
    def execute(self, execution):
        ...


class RequestTemplate(object):
    """
    Hooks for managing the lifecycle of a request.

    To modify behavior of a specific part of the request, override the
    appropriate hook and return the intended transition from
    :mod:`uplink.clients.io.transitions`.

    To fallback to the default behavior, either don't override the hook
    or return :obj:`None` instead, in case of conditional overrides
    (e.g., retry the request if it has failed less than a certain number
    of times).
    """

    def before_request(self, request):
        """
        Handles the request before it is sent.

        Args:
            request: The prospective request data.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """

    def after_response(self, request, response):
        """
        Handles the response after a successful request.

        Args:
            request: The data sent to the server.
            response: The response returned by server.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """

    def after_exception(self, request, exc_type, exc_val, exc_tb):
        """
        Handles the error after a failed request.

        Args:
            request: The attempted request.
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.

        Returns:
            ``None`` or a transition from
            :mod:`uplink.clients.io.transitions`.
        """


class Client(object):
    """An HTTP Client implementation."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, request):
        """
        Sends the given request.

        Args:
            request: The intended request data to be sent.
        """

    @abstractmethod
    def apply_callback(self, callback, response):
        """
        Invokes callback on the response.

        Args:
            callback (callable): a function that handles the response.
            response: data returned from a server after request.
        """


class IOStrategy(object):
    """An adapter for a specific I/O model."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def invoke(self, func, args, kwargs, callback):
        """
        Invokes the given function using the underlying I/O model.

        Args:
            func (callback): The function to invoke.
            args: The function's positional arguments.
            kwargs: The function's keyword arguments.
            callback (:obj:`InvokeCallback`): A callback that resumes
                execution after the invocation completes.
        """

    @abstractmethod
    def sleep(self, duration, callback):
        """
        Pauses the execution for the allotted duration.

        Args:
            duration: The number of seconds to delay execution.
            callback (:obj:`SleepCallback`): A callback that resumes
                execution after the delay.
        """

    @abstractmethod
    def finish(self, response):
        """
        Completes the execution.

        Args:
            response: The object to return to the execution's invoker.
        """

    def fail(self, exc_type, exc_val, exc_tb):
        """
        Fails the execution with a specific error.

        Args:
            exc_type: The exception class.
            exc_val: The exception object.
            exc_tb: The exception's stacktrace.
        """
        compat.reraise(exc_type, exc_val, exc_tb)

    @abstractmethod
    def execute(self, executable):
        """
        Runs a request's execution to completion using the I/O framework
        of this strategy.
        """
