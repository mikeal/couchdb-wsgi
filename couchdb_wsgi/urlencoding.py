# From http://github.com/nshah/python-urlencoding
import cgi
import collections
import urllib


def escape(value):
    """
    Escape the string according to:

    RFC3986: http://tools.ietf.org/html/rfc3986
    http://oauth.net/core/1.0/#encoding_parameters

    Arguments:

        `value`
            The string to escape.

    >>> urlencoding.escape('a b & c')
    'a%20b%20%26%20c'
    >>> urlencoding.escape('abc123-._~')
    'abc123-._~'

    """
    return urllib.quote(value, safe='~')

def is_nonstring_iterable(i):
    return not isinstance(i, basestring) and isinstance(i, collections.Iterable)

def parse_qs(query):
    """
    Parse a query string into a dict. Values my be strings or arrays.

    Arguments:

        `query`
            The query string or form encoded body to parse.

    >>> urlencoding.parse_qs('a=1&b=%20c+d')
    {'a': '1', 'b': ' c d'}
    >>> urlencoding.parse_qs('a=2&a=1')
    {'a': ['2', '1']}

    """
    d = {}
    for k, v in cgi.parse_qs(query, keep_blank_values=False).iteritems():
        if len(v) == 1:
            d[k] = v[0]
        else:
            d[k] = v
    return d

ENCODED_OPEN_BRACKET = escape('[')
ENCODED_CLOSE_BRACKET = escape(']')
def compose_qs(params, sort=False, pattern='%s=%s', join='&', wrap=None):
    """
    Compose a single string using RFC3986 specified escaping using
    `urlencoding.escape`_ for keys and values.

    Arguments:

        `params`
            The dict of parameters to encode into a query string.

        `sort`
            Boolean indicating if the key/values should be sorted.

    >>> urlencoding.compose_qs({'a': '1', 'b': ' c d'})
    'a=1&b=%20c%20d'
    >>> urlencoding.compose_qs({'a': ['2', '1']})
    'a=2&a=1'
    >>> urlencoding.compose_qs({'a': ['2', '1', '3']}, sort=True)
    'a=1&a=2&a=3'
    >>> urlencoding.compose_qs({'a': '1', 'b': {'c': 2, 'd': 3}}, sort=True)
    'a=1&b%5Bc%5D=2&b%5Bd%5D=3'

    """

    if sort:
        params = SortedDict(params)

    pieces = []
    for key, value in params.iteritems():
        escaped_key = escape(str(key))
        if wrap:
            escaped_key = wrap + ENCODED_OPEN_BRACKET + escaped_key + ENCODED_CLOSE_BRACKET

        if isinstance(value, collections.Mapping):
            p = compose_qs(value, sort, pattern, join, escaped_key)
        elif is_nonstring_iterable(value):
            p = join.join([pattern % (escaped_key, escape(str(v))) for v in value])
        else:
            p = pattern % (escaped_key, escape(str(value)))
        pieces.append(p)
    return join.join(pieces)

class SortedDict(dict):
    def iteritems(self):
        """
        Iterates in a sorted fashion. Values are sorted before being yielded if
        they can be. It should result in sorted by key, then value semantics.

        http://oauth.net/core/1.0/#rfc.section.9.1.1

        """
        for key in sorted(self):
            value = self[key]
            if isinstance(value, collections.Mapping):
                value = SortedDict(value)
            elif is_nonstring_iterable(value):
                value = sorted(value)
            yield key, value
