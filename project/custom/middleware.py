class SourceReferrerMidddleware(object):
    """
    Set source referrer on any page
    """
    def process_request(self, request):
        if request.GET.get('sr'):
            request.session['sr'] = request.GET.get('sr')
        return None