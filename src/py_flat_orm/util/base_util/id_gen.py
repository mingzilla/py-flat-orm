import random


class IdGen:
    __LIMIT = 10000
    __MIN_VALUE = -99999999
    __MAX_VALUE = -98999999

    def __init__(self):
        self.__generated_numbers = set()
        self.__random = random.Random()

    @staticmethod
    def create():
        return IdGen()

    def get_int(self):
        if len(self.__generated_numbers) >= IdGen.__LIMIT:
            raise Exception("All unique numbers have been generated")

        new_number = None
        while new_number is None or new_number in self.__generated_numbers:
            new_number = self.__random.randint(IdGen.__MIN_VALUE, IdGen.__MAX_VALUE)

        self.__generated_numbers.add(new_number)
        return new_number

    def clear(self):
        self.__generated_numbers.clear()

    @staticmethod
    def is_generated_id(num):
        try:
            id = int(num)
        except ValueError:
            return False
        return IdGen.__MIN_VALUE <= id <= IdGen.__MAX_VALUE
