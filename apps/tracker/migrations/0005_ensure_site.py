from django.db import migrations
import os

def ensure_site_and_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    
    # 1. Ensure Site exists
    site, created = Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'manvith-finance-tracker-2.onrender.com',
            'name': 'Finance Tracker'
        }
    )
    
    # 2. Ensure SocialApp for Google exists
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    
    if client_id and secret:
        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )
        app.sites.add(site)

class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('socialaccount', '0001_initial'), # Dependency on allauth migration
        ('tracker', '0004_alter_category_type_and_more'),
    ]

    operations = [
        migrations.RunPython(ensure_site_and_app),
    ]
