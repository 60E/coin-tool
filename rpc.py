from proxy import AuthServiceProxy

class BitcoinRPC(object):
    def __init__(self, user, password, host='localhost', port=8332,
                 use_https=False):
        url = 'http{s}://{user}:{password}@{host}:{port}/'.format(
            s='s' if use_https else '',
            user=user, password=password, host=host, port=port)
        self.url = url
        self.proxy = AuthServiceProxy(url)

    def stop(self):
        """
        Stop bitcoin server.
        """
        self.proxy.stop()

    def getinfo(self):
        return self.proxy.getinfo()

    def listunspent(self, minconf=1, maxconf=9999999):
        return [tx for tx in
                self.proxy.listunspent(minconf, maxconf)]


    def sendtoaddress(self, bitcoinaddress, amount, comment=None, comment_to=None):
        """
        Sends *amount* from the server's available balance to *bitcoinaddress*.

        Arguments:

        - *bitcoinaddress* -- Bitcoin address to send to.
        - *amount* -- Amount to send (float, rounded to the nearest 0.01).
        - *minconf* -- Minimum number of confirmations required for transferred balance.
        - *comment* -- Comment for transaction.
        - *comment_to* -- Comment for to-address.

        """
        if comment is None:
            return self.proxy.sendtoaddress(bitcoinaddress, amount)
        elif comment_to is None:
            return self.proxy.sendtoaddress(bitcoinaddress, amount, comment)
        else:
            return self.proxy.sendtoaddress(bitcoinaddress, amount, comment, comment_to)


    def createrawtransaction(self, inputs, outputs):
        """
        Creates a raw transaction spending given inputs
        (a list of dictionaries, each containing a transaction id and an output number),
        sending to given address(es).

        Returns hex-encoded raw transaction.

        Example usage:
        >>> conn.createrawtransaction(
                [{"txid": "a9d4599e15b53f3eb531608ddb31f48c695c3d0b3538a6bda871e8b34f2f430c",
                  "vout": 0}],
                {"mkZBYBiq6DNoQEKakpMJegyDbw2YiNQnHT":50})


        Arguments:

        - *inputs* -- A list of {"txid": txid, "vout": n} dictionaries.
        - *outputs* -- A dictionary mapping (public) addresses to the amount
                       they are to be paid.
        """
        return self.proxy.createrawtransaction(inputs, outputs)

    def signrawtransaction(self, hexstring, previous_transactions=None, private_keys=None):
        """
        Sign inputs for raw transaction (serialized, hex-encoded).

        Returns a dictionary with the keys:
            "hex": raw transaction with signature(s) (hex-encoded string)
            "complete": 1 if transaction has a complete set of signature(s), 0 if not

        Arguments:

        - *hexstring* -- A hex string of the transaction to sign.
        - *previous_transactions* -- A (possibly empty) list of dictionaries of the form:
            {"txid": txid, "vout": n, "scriptPubKey": hex, "redeemScript": hex}, representing
            previous transaction outputs that this transaction depends on but may not yet be
            in the block chain.
        - *private_keys* -- A (possibly empty) list of base58-encoded private
            keys that, if given, will be the only keys used to sign the transaction.
        """
        return self.proxy.signrawtransaction(hexstring, previous_transactions, private_keys)

    def sendrawtransaction(self, hexstring):
        """
        send signed rawtransaction to the Bitcoin network
        returns transaction hash, or an error if the transaction is invalid for any reason
        """
        return self.proxy.sendrawtransaction(hexstring)

