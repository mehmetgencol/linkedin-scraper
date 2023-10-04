from function_handler import FunctionHandler

SEARCH = 'search'
CLEANUP = 'cleanup'
HELP = 'help'
COMPANIES = 'companies'

METHODS = [SEARCH, CLEANUP, HELP, COMPANIES]

function_handler = FunctionHandler()


def handler(event: dict, _):
    method = event.get('method', None)

    if method == SEARCH:
        data = event.get('data', [])
        return function_handler.search(data)

    if method == CLEANUP:
        return function_handler.cleanup()

    if method == COMPANIES:
        return function_handler.companies()

    if method == HELP:
        return function_handler.help()

    return {
        'statusCode': 404,
        'error': f'Unknown method. Use one of {", ".join(METHODS)}'
    }


def test_help():
    event = {'method': HELP}
    return handler(event, None)


def test_companies():
    event = {'method': COMPANIES}
    return handler(event, None)


def test_cleanup():
    event = {'method': CLEANUP}
    return handler(event, None)


def test_empty():
    event = {}
    return handler(event, None)


def test_search():
    event = {'method': SEARCH, 'data': {'company': 'Affirm', 'search_period': 'DAY', 'keywords': 'Software Engineer'}}
    return handler(event, None)


if __name__ == '__main__':
    print('Test Empty result: ', test_empty(), '\n')
    print('Test Help result: ', test_help(), '\n')
    print('Test Companies result: ', test_companies(), '\n')
    print('Test Cleanup result: ', test_cleanup(), '\n')
    print('Test Search result: ', test_search(), '\n')
