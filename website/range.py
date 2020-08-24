from json import loads
def rangeResponse(data):
    """
    takes string request data as input
    outputs trip json
    """
    print(type(data))
    data = loads(data)
    print(type(data))
    return data










data = b'{"dep":"hi","arr":"bye","range":"45"}'
print(rangeResponse(data))