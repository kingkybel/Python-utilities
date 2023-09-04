from abc import ABC, abstractmethod


class TextProcessor(ABC):

    @abstractmethod
    def process(self, original_text: (str | list[str])) -> list:
        pass
