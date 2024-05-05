"""
Creates class from JSON object
"""
import json

class json_object:
    '''
    Universal JSON object
    :param data JSON stored data
    '''
    def __init__(self, data = None):
        if type(data) is str:
            data = json.loads(data)
            for k in data:
                setattr(self, k, data[k])

    def json(self):
        '''
        Serialize class to JSON object
        '''
        return json.dumps(self.__dict__)
