#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='Admin').exists() or (User.objects.create_superuser(username='Admin', email='Admin@gmail.com', password='Admin@1234', role='admin', full_name='Administrator'), print('Superuser Admin created successfully during build', flush=True))"
