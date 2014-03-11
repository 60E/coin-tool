try:
    import http.client as httplib
except ImportError:
    import httplib
import base64
import simplejson
import decimal

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from collections import defaultdict, deque

USER_AGENT = "AuthServiceProxy/0.1"

HTTP_TIMEOUT = 30

class JSONRPCException(Exception):
    def __init__(self, rpc_error):
        Exception.__init__(self)
        self.error = rpc_error


class HTTPTransport(object):
    def __init__(self, service_url):
        self.service_url = service_url
        self.parsed_url = urlparse.urlparse(service_url)
        if self.parsed_url.port is None:
            port = 80
        else:
            port = self.parsed_url.port
        auth_pair = "%s:%s" % (self.parsed_url.username,
                               self.parsed_url.password)
        auth_pair = auth_pair.encode('utf8')
        self.auth_header = "Basic ".encode('utf8') + base64.b64encode(auth_pair)
        if self.parsed_url.scheme == 'https':
            self.connection = httplib.HTTPSConnection(self.parsed_url.hostname,
                                                      port, None, None, False,
                                                      HTTP_TIMEOUT)
        else:
            self.connection = httplib.HTTPConnection(self.parsed_url.hostname,
                                                     port, False, HTTP_TIMEOUT)

    def request(self, serialized_data):
        self.connection.request('POST', self.parsed_url.path, serialized_data,
                                {'Host': self.parsed_url.hostname,
                                 'User-Agent': USER_AGENT,
                                 'Authorization': self.auth_header,
                                 'Content-type': 'application/json'})

        http_resp = self.connection.getresponse()
        if http_resp is None:
            self._raise_exception({
                'code': -342, 'message': 'missing HTTP response from server'})
        elif http_resp.status == httplib.FORBIDDEN:
            msg = "bitcoind returns 403 Forbidden. Is your IP allowed?"
            raise TransportException(msg, code=403,
                                     protocol=self.parsed_url.scheme,
                                     raw_detail=http_resp)

        resp = http_resp.read()
        return resp.decode('utf8')


class RPCMethod(object):
    def __init__(self, name, service_proxy):
        self._method_name = name
        self._service_proxy = service_proxy

    def __getattr__(self, name):
        new_name = '{}.{}'.format(self._method_name, name)
        return RPCMethod(new_name, self._service_proxy)

    def __call__(self, *args):
        self._service_proxy._id_counter += 1
        data = {'version': '1.1',
                'method': self._method_name,
                'params': args,
                'id': self._service_proxy._id_counter}
        post_data = simplejson.dumps(data, use_decimal = True)
        resp = self._service_proxy._transport.request(post_data)
        resp = simplejson.loads(resp, use_decimal = True)

        if resp['error'] is not None:
            self._service_proxy._raise_exception(resp['error'])
        elif 'result' not in resp:
            self._service_proxy._raise_exception({
                'code': -343, 'message': 'missing JSON-RPC result'})
        else:
            return resp['result']

    def __repr__(self):
        return '<RPCMethod object "{name}">'.format(name=self._method_name)


class AuthServiceProxy(object):
    """
    You can use custom transport to test your app's behavior without calling
    the remote service.

    exception_wrapper is a callable accepting a dictionary containing error
    code and message and returning a suitable exception object.
    """

    def __init__(self, service_url, transport=None):
        self._service_url = service_url
        self._id_counter = 0
        self._transport = HTTPTransport(service_url) if transport is None else transport

    def __getattr__(self, name):
        return RPCMethod(name, self)

    def _get_method(self, name):
        """
        Get method instance when the name contains forbidden characters or
        already taken by internal attribute.
        """
        return RPCMethod(name, self)

    def _raise_exception(self, error):
        raise JSONRPCException(error)

