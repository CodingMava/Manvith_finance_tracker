from django.db import migrations

def ensure_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Use update_or_create to ensure it has ID 1
    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'manvith-finance-tracker-2.onrender.com',
            'name': 'Finance Tracker'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'), # Depend on sites initial and follow-up
        ('tracker', '0004_alter_category_type_and_more'), # Last tracker migration
    ]

    operations = [
        migrations.RunPython(ensure_site),
    ]
