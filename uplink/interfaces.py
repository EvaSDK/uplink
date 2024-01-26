# Standard library imports
from abc import ABCMeta, abstractmethod, abstractproperty


class AnnotationMeta(type):
    def __call__(cls, *args, **kwargs):
        if cls._can_be_static and cls._is_static_call(*args, **kwargs):
            self = super(AnnotationMeta, cls).__call__()
            self(args[0])
            return args[0]
        else:
            return super(AnnotationMeta, cls).__call__(*args, **kwargs)


class _Annotation(object):
    _can_be_static = False

    def modify_request_definition(self, request_definition_builder):
        pass

    @classmethod
    def _is_static_call(cls, *args, **kwargs):
        try:
            is_builder = isinstance(args[0], RequestDefinitionBuilder)
        except IndexError:
            return False
        else:
            return is_builder and not (kwargs or args[1:])


Annotation = AnnotationMeta("Annotation", (_Annotation,), {})


class AnnotationHandlerBuilder(object):
    __listener = None
    __metaclass__ = ABCMeta

    @property
    def listener(self):
        return self.__listener

    @listener.setter
    def listener(self, listener):
        self.__listener = listener

    def add_annotation(self, annotation, *args, **kwargs):
        if self.__listener is not None:
            self.__listener(annotation)

    def is_done(self):
        return True

    @abstractmethod
    def build(self):
        ...


class AnnotationHandler(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def annotations(self):
        ...


class UriDefinitionBuilder(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def is_static(self):
        ...

    @abstractproperty
    def is_dynamic(self):
        ...

    @abstractmethod
    @is_dynamic.setter
    def is_dynamic(self, is_dynamic):
        ...

    @abstractmethod
    def add_variable(self, name):
        ...

    @abstractproperty
    def remaining_variables(self):
        ...

    @abstractproperty
    def build(self):
        ...


class RequestDefinitionBuilder(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def method(self):
        ...

    @abstractproperty
    def uri(self):
        ...

    @abstractproperty
    def argument_handler_builder(self):
        ...

    @abstractproperty
    def method_handler_builder(self):
        ...

    @abstractmethod
    def update_wrapper(self, wrapper):
        ...

    @abstractmethod
    def build(self):
        ...

    @abstractmethod
    def copy(self):
        ...


class RequestDefinition(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def make_converter_registry(self, converters):
        ...

    @abstractmethod
    def define_request(self, request_builder, func_args, func_kwargs):
        ...


class CallBuilder(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def client(self):
        ...

    @abstractproperty
    def base_url(self):
        ...

    @abstractproperty
    def converters(self):
        ...

    @abstractproperty
    def hooks(self):
        ...

    @abstractmethod
    def add_hook(self, hook, *more_hooks):
        ...

    @abstractproperty
    def auth(self):
        ...

    @abstractmethod
    def build(self, definition):
        ...


class Auth(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, request_builder):
        ...


class Consumer(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def session(self):
        ...
