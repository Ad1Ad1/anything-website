from django.shortcuts import redirect
from django.urls import reverse

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.profile.is_banned:
                banned_url = reverse('users:banned')
                if request.path != banned_url and not request.path.startswith('/admin/'):
                    if request.path != reverse('users:logout'):
                        return redirect(banned_url)

        return self.get_response(request)
