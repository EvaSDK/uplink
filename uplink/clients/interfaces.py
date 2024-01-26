# Standard library imports
from abc import ABCMeta, abstractmethod

# Local imports
from uplink.clients import exceptions, io


class HttpClientAdapter(io.Client):
    """An adapter of an HTTP client library."""

    __metaclass__ = ABCMeta
    __exceptions = exceptions.Exceptions()

    @abstractmethod
    def io(self):
        """Returns the execution strategy for this client."""

    @property
    def exceptions(self):
        """
        uplink.clients.exceptions.Exceptions: An enum of standard HTTP
        client errors that have been mapped to client specific
        exceptions.
        """
        return self.__exceptions

    @abstractmethod
    def send(self, request):
        ...

    @abstractmethod
    def apply_callback(self, callback, response):
        ...
