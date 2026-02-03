from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def analyze(self, text):
        pass
