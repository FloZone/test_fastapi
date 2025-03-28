from abc import ABC, abstractmethod


class AbstractService(ABC):
    @abstractmethod
    def create(self, object):
        pass

    @abstractmethod
    def delete(self, id: int):
        pass

    @abstractmethod
    def get(self, id: int):
        pass

    @abstractmethod
    def get_list(self, offset: int, limit: int):
        pass

    @abstractmethod
    def update(self, id: int, object):
        pass
