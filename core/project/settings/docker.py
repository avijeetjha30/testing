"""
setting env variable in ubuntu for docker
sudo vim /etc/environment
CORESETTINGS_IN_DOCKER=True
"""
if IN_DOCKER:  # type: ignore  # noqa
    print('running in docker mode')
    assert MIDDLEWARE[:1] == [  # type: ignore # noqa
        'django.middleware.security.SecurityMiddleware'
    ]
