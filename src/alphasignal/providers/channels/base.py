from abc import ABC, abstractmethod

class BaseChannel(ABC):
    @abstractmethod
    def send(self, title, message):
        pass
