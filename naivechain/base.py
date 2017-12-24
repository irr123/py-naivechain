import datetime


class Root(object):

    @staticmethod
    def generate_hash(obj: str) -> int:
        return hash(obj)

    @staticmethod
    def generate_timestamp() -> float:
        return datetime.datetime.timestamp(datetime.datetime.now())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class Singleton(Root):

    _instances = {}

    def __init__(self, class_obj) -> None:
        self.class_obj = class_obj

    def __call__(self, *args, **kwargs):
        if self.class_obj.__name__ not in self._instances:
            self._instances[self.class_obj.__name__] = \
                self.class_obj(*args, **kwargs)
        return self._instances[self.class_obj.__name__]

    def __str__(self) -> str:
        return f"{self._instances[self.class_obj.__name__]}"

    def __getattr__(self, attr):
        return getattr(self._instances[self.class_obj.__name__], attr)
