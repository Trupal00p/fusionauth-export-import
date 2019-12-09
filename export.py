import argparse
import json
from common import get_config

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

args = parser.parse_args()

config_json = get_config(args.url, args.apikey)

with open('fusion-config.json', 'w') as config:
    config.write(json.dumps(config_json, **{
        'indent': 4,
        'sort_keys': True,
        'separators': (',', ': ')
    }))
