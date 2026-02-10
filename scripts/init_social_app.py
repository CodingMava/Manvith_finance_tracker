import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

try:
    # Ensure current site matches SITE_ID
    site = Site.objects.get(id=settings.SITE_ID)
    print(f"Current Site: {site.domain}")

    # Check for Google SocialApp
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        name='Google Login'
    )
    
    app.client_id = settings.GOOGLE_OAUTH_CLIENT_ID or 'placeholder-id'
    app.secret = settings.GOOGLE_OAUTH_CLIENT_SECRET or 'placeholder-secret'
    app.save()

    if created:
        app.sites.add(site)
        print("Google SocialApp created and linked to site.")
    else:
        print("Google SocialApp updated with current credentials.")
        
except Exception as e:
    print(f"Error initializing SocialApp: {e}")
