from django.db import migrations
import os

def fix_site_and_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    
    # Get domain from environment or default
    domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'manvith-finance-tracker-4.onrender.com')
    
    # 1. Update/Create Site (ID 1)
    site, _ = Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': domain,
            'name': 'Finance Tracker'
        }
    )
    
    # 2. Update/Create SocialApp for Google
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    
    if client_id and secret:
        # Avoid MultipleObjectsReturned by starting fresh
        SocialApp.objects.filter(provider='google').delete()
        
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret,
        )
        app.sites.add(site)

class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0005_ensure_site'), # Depend on the previous failed attempt
    ]

    operations = [
        migrations.RunPython(fix_site_and_app),
    ]
