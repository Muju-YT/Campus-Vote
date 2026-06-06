"""
WSGI config for CampusVote project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CampusVote.settings')

application = get_wsgi_application()

# Auto-create superuser on startup
try:
    import sys
    if 'test' not in sys.argv:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='Admin',
                email='Admin@gmail.com',
                password='Admin@1234',
                role='admin'
            )
            print(">>> Auto-created superuser 'Admin'")
except Exception as e:
    print(f">>> Superuser auto-creation skipped: {e}")
