from enum import Enum


class TestEnum(Enum):
    ONE = ('ONE', '1')
    TWO = ('TWO', '2')
    THREE = ('THREE', '3')

    @property
    def name(self):
        return self.value[0]

    @property
    def value(self):
        return self._value_

    def __init__(self, name, value):
        self._value_ = value  # Assigning value to the enum member

    def __str__(self):
        return f'{self.name}'
