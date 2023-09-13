import json

from function_handler import FunctionHandler

SEARCH = 'search'
CLEANUP = 'cleanup'
HELP = 'help'
COMPANIES = 'companies'

METHODS = [SEARCH, CLEANUP, HELP, COMPANIES]

function_handler = FunctionHandler()


def handler(event, _):
    data = json.loads(event['body'])
    method = data["method"]

    if method == SEARCH:
        return function_handler.search(data)

    if method == CLEANUP:
        return function_handler.cleanup(data)

    if method == COMPANIES:
        return function_handler.companies()

    if method == HELP:
        return function_handler.help()

    return {
        'statusCode': 404,
        'error': f'Unknown method. Use one of {", ".join(METHODS)}'
    }
