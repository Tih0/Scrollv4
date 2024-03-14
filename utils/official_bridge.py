from client import Client, TokenAmount, logger
from utils.contracts import contract_official_bridge
from utils.read_json import read_json
from config import TOKEN_OFFICIAL_BRIDGE
import time
from web3 import Web3
from web3.exceptions import TransactionNotFound
class OfficialBridge:
    abi = read_json(TOKEN_OFFICIAL_BRIDGE)
    def __init__(self, client: Client, maxGas: int):
        self.client = client
        self.maxGas = maxGas
    def bridge(self, amount: TokenAmount, retry = 0):
        print(f"{self.client.address} | Official Bridge  | {format(amount.Ether, '.4f')} ETH")
        logger.info(f"{self.client.address} | Official Bridge  | {format(amount.Ether, '.4f')} ETH")
        try:
            contract = self.client.w3.eth.contract(address=contract_official_bridge, abi=OfficialBridge.abi)
            tx = self.client.send_transaction(
                eip1559=True,
                to= contract_official_bridge,
                data= contract.encodeABI("depositETH", params= (
                    amount.Wei,
                    NULL,
                    168000      # gasLimit const (will need to check this param when contract update)
                )),
                value= amount.Wei,
            )
            print("Ожидаем подтверждение транзакции")
            time.sleep(30)
            verify = self.client.verif_tx(tx)
            if verify == False:
                retry += 1
                if retry < 5:
                    print(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    logger.error(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    print('Time sleep 20 seconds')
                    time.sleep(20)
                    self.bridge(amount, retry)

        except TransactionNotFound:
            print(f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            logger.error(f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            print('Time sleep 120 seconds')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(amount, retry)


        except ConnectionError:
            print(f'{self.client.address} | Internet connection error or problems with the RPC')
            logger.error(f'{self.client.address} | Internet connection error or problems with the RPC')
            time.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            self.bridge(amount, retry)

        except Exception as error:
            print(f"{self.client.address} | Unknown Error:  {error} \n Mayber not Gas")
            logger.error(f"{self.client.address} | Unknown Error:  {error}")
            print('Time sleep 120 seconds')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.bridge(amount, retry)


