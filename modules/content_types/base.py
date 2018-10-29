from pprint import pprint
from abc import ABC, abstractmethod

class ContentTypes_Base(ABC):
    
    @abstractmethod
    def do_something(self):
        print("Some implementation!")

