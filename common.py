import requests


def get_config(url, apikey):

    endpoints = [
        '/api/application',
        '/api/group',

        '/api/email/template',
        '/api/theme',
        '/api/tenant',
        '/api/lambda',
        '/api/user-action',
        '/api/user-action-reason',
        '/api/webhook',

        '/api/system-configuration',
        '/api/integration',

    ]
    results = {}

    for endpoint in endpoints:
        response = requests.get(
            '{}{}'.format(url, endpoint),
            data="{}",
            headers={
                'Authorization': apikey,
                'Content-Type': 'application/json'
            }
        )

        results[endpoint] = response.json()

    # remove fusion auth default app
    results['/api/application']['applications'] = [
        app for app in results['/api/application']['applications']
        if app['oauthConfiguration'].get('logoutURL', '') != '/'
    ]

    # remove fusion auth default theme
    results['/api/theme']['themes'] = [
        app for app in results['/api/theme']['themes']
        if app['name'] != 'FusionAuth'
    ]

    return results
