from client import Client, TokenAmount, logger
from utils.contracts import contract_owlto
import time
from web3 import Web3
from web3.exceptions import TransactionNotFound
class Owlto:
    def __init__(self, client: Client, maxGas: int):
        self.client = client
        self.maxGas = maxGas
    def defference(self, amount: int):
        amount = str(amount)
        amount = amount[:-1]
        amount += '6'
        if amount[len(amount) - 3] == '9':
            amount = self.defference(int(amount) + 10)
        return int(amount)
    def bridge(self, amount: TokenAmount, retry = 0):
        print(f"{self.client.address} | Owlto Bridge | {format(amount.Ether, '.4f')} ETH")
        logger.info(f"{self.client.address} | Owlto Bridge | {format(amount.Ether, '.4f')} ETH")
        try:
            value = self.defference(amount.Wei)
            tx = self.client.send_transaction(
                eip1559=True,
                to= contract_owlto,
                value= value,
            )

            time.sleep(5)
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


