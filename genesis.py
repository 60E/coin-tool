from rpc import BitcoinRPC
from decimal import Decimal

bitcoind = BitcoinRPC('naituida','123','localhost',8088)

GENESIS_ADDR = "FoipmNrZ5wARHJoszB4ZDHMoVtZ1TCSy2K"

START_BLOCK = 0
END_BLOCK = 1000

for blockheight in xrange(START_BLOCK,END_BLOCK):
    blockhash = bitcoind.getblockhash(blockheight)
#    print blockhash
    block = bitcoind.getblock(blockhash)
#    print block
    txs = block['tx']
    for txid in txs:
        tx = bitcoind.getrawtransaction(txid)
        raw_tx = bitcoind.decoderawtransaction(tx)
        outputs = raw_tx['vout']
        for output in outputs:
            addr =  output['scriptPubKey']['addresses'][0]
            if addr == GENESIS_ADDR:
                print txid


        
                
    

