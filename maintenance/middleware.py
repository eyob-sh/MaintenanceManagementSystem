# maintenance/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, Resolver404, reverse

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # First get the response
        response = self.get_response(request)
        
        # Check if path is protected and user is not authenticated
        if not request.user.is_authenticated and self._is_protected_path(request.path):
            # Verify the login URL exists before redirecting
            try:
                resolve(reverse('login'))
                return redirect('login')
            except:
                # Fallback to /login/ if reverse fails
                return redirect('/login/')

        # Add cache headers for authenticated users
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response

    def _is_protected_path(self, path):
        # More robust path checking that handles:
        # - Different URL patterns
        # - Query parameters
        # - Optional trailing slashes
        
        unprotected_paths = ['/login/', '/logout/', '/admin/login/']
        
        # Check if path starts with any protected prefix
        protected_prefixes = [
            '/dashboard', 
            '/inventory',
            '/client',
            '/maintenance',
            # Add all other protected prefixes
        ]
        
        # Exclude static/media files
        if path.startswith(('/static/', '/media/')):
            return False
            
        # Check if path should be protected
        return (not any(path.startswith(p) for p in unprotected_paths) and
                any(path.startswith(p) for p in protected_prefixes))