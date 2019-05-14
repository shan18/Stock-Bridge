from django.contrib.sessions.models import Session


class OneSessionPerUserMiddleware:
    """ Called only once when the web server starts """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """ Code to be executed for each request before
            the views (and later middleware) are called.
        """
        # if request.user.is_authenticated:
        #     stored_session_key = request.user.loggedinuser.session_key

        #     # If there is a stored_session_key in the database and it is
        #     # different from the current session key then delete the session
        #     # with the stored_session_key from the Session table
        #     if stored_session_key and stored_session_key != request.session.session_key:
        #         Session.objects.get(session_key=stored_session_key).delete()

        #     request.user.loggedinuser.session_key = request.session.session_key
        #     request.user.loggedinuser.save()
        
        response = self.get_response(request)
        return response
    