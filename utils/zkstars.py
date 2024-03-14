import random
import time, sys
from web3.exceptions import TransactionNotFound
from web3 import Web3
from client import Client, TokenAmount, logger
from config import TOKEN_ZKSTARS
from utils.read_json import read_json
from utils.contracts import contractsZKStars
import asyncio
class ZkStars:
    abi = read_json(TOKEN_ZKSTARS)

    def __init__(self, client: Client, maxGas):
        self.client = client
        self.maxGas = maxGas

    async def mintZkStars(self, contract_star: str,  retry=0):
        try:
            contract = self.client.w3.eth.contract(address=contract_star, abi=ZkStars.abi)
            amount = contract.functions.getPrice().call()
            name = contract.functions.name().call()
            print(f'{self.client.address} | mint {name}...')
            logger.info(f'{self.client.address} | mint {name}...')
            tx = self.client.send_transaction(
                to=contract_star,
                data=contract.encodeABI('safeMint',
                                        args=[self.client.address]
                                        ),
                value=amount
            )

            await asyncio.sleep(5)
            verify = self.client.verif_tx(tx)
            if verify == False:
                retry += 1
                if retry < 5:
                    print(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    logger.error(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    print('Time sleep 20 seconds')
                    asyncio.sleep(20)
                    await self.mintZkStars(contract_star, retry)

                else:
                    print(f"ERROR MINT")
                    logger.error(f"{self.client.address} | ERROR MINT")
                    return 0


        except TransactionNotFound:
            print(
                f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            logger.error(
                f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            await self.mintZkStars(contract_star, retry)


        except ConnectionError:
            print(f'{self.client.address} | Internet connection error or problems with the RPC')
            logger.error(f'{self.client.address} | Internet connection error or problems with the RPC')
            await asyncio.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            await self.mintZkStars(contract_star, retry)

        except Exception as error:
            print(f"{self.client.address} | Unknown Error:  {error} \n Mayber not Gas")
            logger.error(f'{self.client.address} | Unknown Error:  {error}')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)

            retry += 1
            if retry > 5:
                return 0
            await self.mintZkStars(contract_star, retry)

