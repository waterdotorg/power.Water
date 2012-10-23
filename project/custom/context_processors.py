def returning_user(request):
    if request.COOKIES.get('returning_user'):
        return {'returning_user': True}
    else:
        return {'returning_user': False}