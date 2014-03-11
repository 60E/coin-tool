from rpc import BitcoinRPC
from decimal import Decimal

bitcoind = BitcoinRPC('naituida','123','localhost',8088)

def send_from_local(from_addresses, payments, change_address, min_conf=6, wallet_pwd=None):
    _payments = {}
    for address, amount in payments.iteritems():
        _payments[address] = Decimal(amount)
    payments = _payments

    fee = bitcoind.getinfo()['paytxfee']

    unspent = [t for t in bitcoind.listunspent(minconf = min_conf) if t['address'] in from_addresses]

    send_sum = sum(payments.values())
    unspent_sum = sum([t['amount'] for t in unspent])

    if unspent_sum < send_sum + fee:
        print "Not enough fund!"
        exit()

    #select unspent
    unspent.sort(key=lambda t: t['confirmations'], reverse=True)

    chosen = []
    for t in unspent:
        if sum([c['amount'] for c in chosen]) < send_sum + fee:
            chosen.append(t)
        else:
            break

    change = sum([c['amount'] for c in chosen]) - fee - send_sum

    if change_address in payments:
        print "Change address already in payments"
        exit()
    payments[change_address] = change

    #compose raw transaction
    raw_tx = bitcoind.createrawtransaction([{'txid':c['txid'], 'vout':c['vout']} for c in chosen], payments)

    try:
        if wallet_pwd:
            bitcoind.walletlock()  # lock the wallet so we make sure it has sufficient time in the later process
            bitcoind.walletpassphrase(wallet_pwd, 10)  # unlock the wallet

        sign_rst = bitcoind.signrawtransaction(raw_tx)
        if sign_rst['complete'] == 0:
            print "Error signing raw tx"
            exit()

        tx_hash = bitcoind.sendrawtransaction(sign_rst['hex'])
        
        return tx_hash
    finally:
        if wallet_pwd:
            bitcoind.walletlock()


# demo
#                         list of from addresses               list of receive address and amount              change address
# print send_from_local(["mkdrh9x5tY4umq2SkPv9WxgoAkbcqtouV5"],{"mwvVa5mqNEVEyrTSZsjCnNWv4vufSxP44L":"1000.1"},"mkdrh9x5tY4umq2SkPv9WxgoAkbcqtouV5")
