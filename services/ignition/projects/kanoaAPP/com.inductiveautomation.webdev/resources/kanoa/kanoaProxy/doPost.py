def doPost(request, session):

    import json
    data = request['data']
    ret = {'json': {"kanoa": "ok"}}
    system.kanoa.config.setKanoaConfigData(data)
    return ret