import datetime
import hashlib


DEBUG = False


class Root(object):

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class NaiveChainException(Root, Exception):
    pass


class ISerializable(Root):

    @classmethod
    def deserialize(cls, data: str) -> 'ISerializable':
        raise NotImplementedError

    def serialize(self) -> str:
        raise NotImplementedError


class LoggedRoot(Root):

    @classmethod
    def log(cls, *args, **kwargs) -> None:
        if DEBUG:
            print(f"[{cls.__name__}]:", *args, **kwargs)


class NaiveChainObj(Root):

    @staticmethod
    def generate_hash(obj: str) -> str:
        return hashlib.sha224(obj.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_timestamp() -> float:
        return datetime.datetime.timestamp(datetime.datetime.now())


class LoggedNaiveChain(LoggedRoot, NaiveChainObj):
    pass


class Singleton(LoggedNaiveChain):

    _instances = {}

    def __init__(self, class_obj) -> None:
        self.class_obj = class_obj

    def __call__(self, *args, **kwargs):
        if self.class_obj.__name__ not in self._instances:
            self._instances[self.class_obj.__name__] = \
                self.class_obj(*args, **kwargs)
            self.log('New instance of', self.class_obj.__name__)
        return self._instances[self.class_obj.__name__]

    def __str__(self) -> str:
        return f"{self._instances[self.class_obj.__name__]}"

    def __getattr__(self, attr):
        return getattr(self._instances[self.class_obj.__name__], attr)
