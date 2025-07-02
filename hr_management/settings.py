import os
env = os.environ.get('DJANGO_ENV', 'development')
if env == 'production':
    from .config.production import *
elif env == 'base':
    from .config.base import *
else:
    from .config.development import *