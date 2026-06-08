"""
WSGI config for CampusVote project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CampusVote.settings')

application = get_wsgi_application()

# Auto-create superuser on startup
if 'test' not in sys.argv:
    try:
        import logging
        logger = logging.getLogger('django')
        from django.contrib.auth import get_user_model
        from django.db import transaction, IntegrityError
        User = get_user_model()
        
        # Check if user with username 'Admin' already exists
        if User.objects.filter(username='Admin').exists():
            msg = "Superuser Admin already exists"
            print(msg, flush=True)
            logger.info(msg)
        else:
            try:
                with transaction.atomic():
                    User.objects.create_superuser(
                        username='Admin',
                        email='Admin@gmail.com',
                        password='Admin@1234',
                        role='admin',
                        full_name='Administrator'
                    )
                msg = "Superuser Admin created successfully"
                print(msg, flush=True)
                logger.info(msg)
            except IntegrityError:
                # Handle race condition where another Gunicorn worker created it simultaneously
                msg = "Superuser Admin already exists"
                print(msg, flush=True)
                logger.info(msg)
    except Exception as e:
        msg = f"Superuser Admin creation failed: {e}"
        print(msg, flush=True)
        logger.error(msg)
