import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buy_n_large.settings")

application = get_wsgi_application()
