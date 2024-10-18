import typing

import aiohttp


class CheckPaymentTyping:
    notpayed = 'notpayed'
    processing = 'processing'
    payed = 'payed'


class CrystalPay:
    def __init__(self, secret_1: str, secret_2: str, login):
        self.secret_1 = secret_1
        self.secret_2 = secret_2
        self.login = login

        self._api_url = "https://api.crystalpay.ru/v3/"

    async def create_payment_url(self, amount: int, lifetime=60) -> typing.Tuple[str, str]:
        params = dict(o='invoice-create', s=self.secret_1, n=self.login,
                      amount=amount, lifetime=lifetime)

        async with aiohttp.ClientSession() as session:
            response = await session.get(self._api_url, params=params)
            data = await response.json()

            return data.get('id'), data.get('url')

    async def check_payment(self, payment_id: str):
        params = {
            "o": 'invoice-check',
            'n': self.login,
            's': self.secret_1,
            'i': payment_id
        }

        async with aiohttp.ClientSession() as session:
            response = await session.get(self._api_url, params=params)
            data = await response.json()

            return data.get('amount'), data.get('state')
