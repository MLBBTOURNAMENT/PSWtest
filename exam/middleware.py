from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'participantprofile'):
            if request.user.participantprofile.blocked:
                logout(request)
                return redirect('/?blocked=true')
        
        response = self.get_response(request)
        return response
