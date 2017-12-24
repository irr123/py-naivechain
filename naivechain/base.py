import datetime


DEBUG = False


class Root(object):

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class NaiveChainException(Root, Exception):
    pass


class NaiveChainObj(Root):

    @staticmethod
    def log(*args, **kwargs) -> None:
        if DEBUG:
            print(*args, **kwargs)

    @staticmethod
    def generate_hash(obj: str) -> int:
        return hash(obj)

    @staticmethod
    def generate_timestamp() -> float:
        return datetime.datetime.timestamp(datetime.datetime.now())


class LoggedNaiveChain(NaiveChainObj):

    def log(self, *args, **kwargs):
        super().log(
            f"[{super().__str__()}]: ",
            *args, **kwargs
        )


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
