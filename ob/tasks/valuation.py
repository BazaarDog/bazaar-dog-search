from time import sleep
from ob.util import get_exchange_rates, update_price_values


def update_price_values():
    get_exchange_rates()
    sleep(3)
    update_price_values()
