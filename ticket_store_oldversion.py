#Felix Hommels Submission
from datetime import datetime
import time
from typing import List, Dict, Tuple, Callable
from threading import Thread, Semaphore


INITIAL_TIMESTAMP = datetime.now()


def get_elapsed_seconds() -> float:
    return round((datetime.now() - INITIAL_TIMESTAMP).total_seconds(), 1)


def simulate_store(customers: List[Dict], ticket_price: float, max_occupancy: int, n_vips: int) -> float:
    store = Store(ticket_price, max_occupancy)
    customer_threads = []

    vip_customers = [customer for customer in customers if customer["VIP"] is True]
    normal_customers = [customer for customer in customers if customer["VIP"] is False]

    for person in vip_customers:
        customer = Customer(person["name"],person["ticketCount"],person["timeInStore"],person["joinDelay"],person["VIP"], store)
        customer_threads.append(customer)
        customer.start()

    for customer in customer_threads:
        customer.join()

    customer_threads.clear()

    for person in normal_customers:
        customer = Customer(person["name"],person["ticketCount"],person["timeInStore"],person["joinDelay"],person["VIP"], store)
        customer_threads.append(customer)
        customer.start()

    for customer in customer_threads:
        customer.join()

    return store.earnings


class Customer(Thread): #Customer Behaviour Class
    def __init__(self, name, ticketCount, timeInStore, joinDelay, vip, store):
        super().__init__(name=name)
        self.ticketCount = ticketCount
        self.timeInStore = timeInStore
        self.joinDelay = joinDelay
        self.vip = vip
        self.store = store

    def run(self):
        time.sleep(self.joinDelay)
        self.store.enter_store(self)
        time.sleep(self.timeInStore)
        self.store.purchase_tickets(self.ticketCount)
        self.store.leave(self)


class Store:
    def __init__(self, ticketPrice, max_occupancy):
        self.ticketPrice = ticketPrice
        self.max_occupancy = max_occupancy
        self.earnings = 0
        self.earnings_semaphore = Semaphore(value=1)
        self.semaphore = Semaphore(max_occupancy)

    def enter_store(self, customer):
        self.semaphore.acquire()
        print(f"{get_elapsed_seconds()}s: {customer.name} (Entering)")

    def leave(self, customer):
        self.semaphore.release()
        print(f"{get_elapsed_seconds()}s: {customer.name} (Leaving)")

    def purchase_tickets(self, ticketCount):
        self.earnings_semaphore.acquire()
        self.earnings += self.ticketPrice * ticketCount
        self.earnings_semaphore.release()
        