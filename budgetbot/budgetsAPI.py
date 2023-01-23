from requests import post, get, delete
from conf import DOMAIN

class APIHandler():

    def request(requestType, objectType, command, pk = '', data = {}):
        resp = None
        try:
            resp = requestType(f'{DOMAIN}{objectType}/{command}/{pk}', json = data)
            return resp.json()
        except:
            if resp:
                return resp.status_code
            return False

    def create(objectType, data):
        return APIHandler.request(post, objectType, 'create', data = data)
    
    def read(objectType, pk, data = {}):
        return APIHandler.request(get, objectType, 'list', pk, data)

    def update(objectType, pk, data):
        return APIHandler.request(post, objectType, 'update', pk, data)

    def delete(objectType, pk):
        return APIHandler.request(delete, objectType, 'delete', pk)