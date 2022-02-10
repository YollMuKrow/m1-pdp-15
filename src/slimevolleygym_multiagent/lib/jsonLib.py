import json


class jsonInput:

    def __init__(self, file_name='env.json'):
        """Constructs the configuration dictionary with the json data in it"""
        self.__cfg_dct = {}
        file = open(file_name, 'r')
        data = file.read()
        self.__cfg_dct = json.loads(data)
        file.close()

    def get_value_from_Json(self, *arg):
        """
        Goes through the json tree according to the args

        Return the value associated
        """
        res = self.__cfg_dct[arg[0]]
        if len(arg) == 1:
            return res
        for i in range(1, len(arg)):
            res = res[arg[i]]
        return res
