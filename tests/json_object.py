import json
import base64

class json_object(object):
    '''
    Universal JSON object
    :param data JSON stored data
    '''
    def __init__(self, data = None):
        super().__init__()
        if type(data) is str:
             self.__dict__ = json.loads(data)

    def json(self):
        '''
        Serialize class to JSON object
        '''
        return json.dumps(self, default=self._default, sort_keys=True, indent=4)


    @staticmethod
    def _default(o):
        if type(o) is bytes:
            return base64.b64encode(o).decode("utf-8")
        return o.__dict__
        