def doGet(request, session):

    import json
    data = system.kanoa.config.getKanoaConfigData()
    return {'json': json.loads(data)}