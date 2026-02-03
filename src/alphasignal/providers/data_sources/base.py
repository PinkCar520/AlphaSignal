from abc import ABC, abstractmethod

class BaseDataSource(ABC):
    @abstractmethod
    def fetch(self):
        """
        获取最新数据
        Returns:
            dict or None: {
                "id": str,
                "content": str,
                "url": str,
                "source": str,
                "timestamp": str
            }
        """
        pass
