import argparse
import requests
import json
from common import get_config
from jsondiff import diff, patch, similarity, JsonDumper

parser = argparse.ArgumentParser()
parser.add_argument(
    '--apikey',
    help='API key for Fusion Auth instance.',
    required=False,
    # dont get too excited this API key is from an old dev instance :)
    default='av2sjd077G32obL5tuTpG-kw38-wQXW2eHLaccf9938'
)
parser.add_argument(
    '--url',
    help='URL of Fusion Auth instance.',
    required=False,
    default='http://172.17.228.43:30941'
)
parser.add_argument(
    '--configfile',
    help='path to exported config data.',
    required=False,
    default='./fusion-config.json'
)

args = parser.parse_args()

base_headers = {
    'Authorization': args.apikey,
    'Content-Type': 'application/json',
}


def merge_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def handle_response(response, config):
    try:
        assert response.status_code == 200
    except AssertionError:
        print 'Error:', response.status_code
        print response.content
        print config['id']


def create_requests(endpoint, name):
    def create_request(config):
        response = requests.post(
            '{}{}/{}'.format(args.url, endpoint, config['id']),
            data=json.dumps({name: config}),
            headers=base_headers
        )
        handle_response(response, config)

    def update_request(config):
        response = requests.put(
            '{}{}/{}'.format(args.url, endpoint, config['id']),
            data=json.dumps({name: config}),
            headers=base_headers
        )
        handle_response(response, config)

    def delete_request(application):
        response = requests.delete(
            '{}{}/{}'.format(args.url, endpoint, config['id']),
            data="{}",
            headers=base_headers
        )
        handle_response(response, config)

    return (create_request, update_request, delete_request)


def generate_apply_args(saved, existing, endpoint, name):
    try:
        saved_configs = saved[endpoint]["{}s".format(name)]
    except KeyError:
        saved_configs = []
    try:
        existing_configs = existing[endpoint]["{}s".format(name)]
    except KeyError:
        existing_configs = []

    return [
        name,
        saved_configs,
        existing_configs,
    ] + list(create_requests(endpoint, name))


def apply_saved(
    name,
    saved_build,
    existing_build,
    create_request,
    update_request,
    delete_request
):
    # print "Checking for {} changes...".format(name)
    saved_indexed = {
        config['id']: config
        for config
        in saved_build
    }
    saved_ids = set(saved_indexed.keys())

    existing_indexed = {
        config['id']: config
        for config
        in existing_build
    }
    exisiting_ids = set(existing_indexed.keys())

    create_ids = saved_ids - exisiting_ids
    update_ids = saved_ids & exisiting_ids
    delete_ids = exisiting_ids - saved_ids

    # if not create_ids and not update_ids and not delete_ids:
    #     print 'No changes detected.'
    #     return

    for id in create_ids:
        print 'Creating: ', id, '...'
        create_request(saved_indexed[id])

    for id in update_ids:
        if similarity(saved_indexed[id], existing_indexed[id]) < 1:
            print "Updating: ", id, '...'
            update_request(saved_indexed[id])

    for id in delete_ids:
        print "Deleting: ", id, '...'
        delete_request(saved_indexed[id])


print "Pulling config from server ..."
existing_config = get_config(args.url, args.apikey)

print 'Loading saved config from file system ...'
with open(args.configfile, 'r') as config:
    saved_config = json.loads(config.read())

# '/api/application',
_, update_application_request, delete_application_request = create_requests(
    '/api/application',
    'application'
)


def create_application_request(application):
    tenantId = application.pop('tenantId')
    requests.post(
        '{}{}/{}'.format(args.url, '/api/application', application['id']),
        data=json.dumps({'application': application}),
        headers=merge_dicts(
            base_headers,
            {
                'X-FusionAuth-TenantId': tenantId
            }
        )
    )


apply_saved(
    'application',
    saved_config['/api/application']["applications"],
    existing_config['/api/application']["applications"],
    create_application_request,
    update_application_request,
    delete_application_request
)

# '/api/application/id/roles'
saved_roles = []
for application in saved_config['/api/application']['applications']:
    for role in application.get('roles', []):
        saved_roles.append(merge_dicts(role, {
            'appId': application['id']
        }))

existing_roles = []
for application in saved_config['/api/application']['applications']:
    for role in application.get('roles', []):
        existing_roles.append(merge_dicts(role, {
            'appId': application['id']
        }))


def create_role_request(config):
    appId = config.pop('appId')
    response = requests.post(
        '{}/api/application/{}/role'.format(args.url, appId),
        data=json.dumps({'role': config}),
        headers=base_headers
    )
    handle_response(response, config)


def update_role_request(config):
    appId = config.pop('appId')
    response = requests.put(
        '{}/api/application/{}/role/{}'.format(args.url, appId, config['id']),
        data=json.dumps({'role': config}),
        headers=base_headers
    )
    handle_response(response, config)


def delete_role_request(application):
    appId = config.pop('appId')
    response = requests.delete(
        '{}/api/application/{}/role/{}'.format(args.url, appId, config['id']),
        data="{}",
        headers=base_headers
    )
    handle_response(response, config)


apply_saved(
    'role',
    saved_roles,
    existing_roles,
    create_role_request,
    update_role_request,
    delete_role_request
)

# '/api/group',
_, update_group_request, delete_group_request = create_requests(
    '/api/group',
    'group'
)


def create_group_request(group):
    tenantId = group.pop('tenantId')
    requests.post(
        '{}{}/{}'.format(args.url, '/api/group', group['id']),
        data=json.dumps({'group': group}),
        headers=merge_dicts(
            base_headers,
            {
                'X-FusionAuth-TenantId': tenantId
            }
        )
    )


try:
    saved_groups = saved_config['/api/groups']["groups"]
except KeyError:
    saved_groups = []
try:
    exising_groups = existing_config['/api/groups']["groups"]
except KeyError:
    exising_groups = []

apply_saved(
    'group',
    saved_groups,
    exising_groups,
    create_application_request,
    update_application_request,
    delete_application_request
)


standard = [
    ('/api/email/template', 'emailTemplate'),
    ('/api/tenant', 'tenant'),
    ('/api/theme', 'theme'),
    ('/api/lambda', 'lambda'),
    ('/api/user-action-reason', 'userActionReason'),
    ('/api/user-action', 'userAction'),
    ('/api/webhook', 'webhook'),
]
for endpoint, name in standard:
    apply_saved(
        *generate_apply_args(
            saved_config,
            existing_config,
            endpoint,
            name
        )
    )


# update system config
if similarity(
    saved_config['/api/system-configuration']["systemConfiguration"],
    existing_config['/api/system-configuration']["systemConfiguration"]
) < 1:
    print 'Applying system configuration changes...'
    response = requests.put(
        '{}/api/system-configuration'.format(args.url),
        data=json.dumps({
            'systemConfiguration': saved_config['/api/system-configuration']["systemConfiguration"]
        }),
        headers=base_headers
    )
    handle_response(response, config)

# update integrations config
if similarity(
    saved_config['/api/integration']["integrations"],
    existing_config['/api/integration']["integrations"]
) < 1:
    print 'Applying integrations configuration changes...'
    response = requests.put(
        '{}/api/integration'.format(args.url),
        data=json.dumps({
            'integrations': saved_config['/api/integration']["integrations"]
        }),
        headers=base_headers
    )
    handle_response(response, config)

print "Done!"
