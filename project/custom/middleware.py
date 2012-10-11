class ReferrerMidddleware(object):
    """
    Set referrer on any page
    """
    def process_request(self, request):
        # Source Referrer
        if request.GET.get('sr'):
            request.session['sr'] = request.GET.get('sr')

        # User Referrer
        if request.GET.get('ur'):
            request.session['ur'] = request.GET.get('ur')

        return None