from abc import abstractmethod


class Repository:
    @abstractmethod
    def create(self, data):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id):
        raise NotImplementedError

    @abstractmethod
    def update(self, id, data):
        raise NotImplementedError

    @abstractmethod
    def delete(self, id):
        raise NotImplementedError
