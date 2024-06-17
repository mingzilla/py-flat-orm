from enum import Enum


class TestEnum(Enum):
    ONE = ('ONE', '1')
    TWO = ('TWO', '2')
    THREE = ('THREE', '3')

    def __init__(self, name, value):
        self.name = name
        self.value = value
