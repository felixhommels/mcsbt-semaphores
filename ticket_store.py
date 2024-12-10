#Felix Hommels Submission
from datetime import datetime
import time
from typing import List, Dict, Tuple, Callable
from threading import Thread, Semaphore


INITIAL_TIMESTAMP = datetime.now()


def get_elapsed_seconds() -> float:
    return round((datetime.now() - INITIAL_TIMESTAMP).total_seconds(), 1)


def simulate_store(customers: List[Dict], ticket_price: float, max_occupancy: int, n_vips: int) -> float:
    vip_customers = [customer for customer in customers if customer["VIP"] is True]
    normal_customers = [customer for customer in customers if customer["VIP"] is False]
    customer_threads = []

    store = Store(ticket_price, max_occupancy, vip_customers)

    for person in vip_customers:
        customer = Customer(person["name"],person["ticketCount"],person["timeInStore"],person["joinDelay"],person["VIP"], store)
        customer_threads.append(customer)
        customer.start()

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
    def __init__(self, ticketPrice, max_occupancy, vip_customers):
        self.ticketPrice = ticketPrice
        self.max_occupancy = max_occupancy
        self.earnings = 0
        self.earnings_semaphore = Semaphore(value=1)
        self.semaphore = Semaphore(max_occupancy)        
        self.regular_access_semaphore = Semaphore(0)      
        self.vip_count = 0
        self.number_of_vip = len(vip_customers)
        self.check_number_vips()
    
    #Handling the edge case if there are no vips at all -> need to release the semaphore for regular customers to enter the store
    #No need to handle edge case of only vips since we are not using the regular_access_semaphore in that case
    def check_number_vips(self):
        if self.number_of_vip == 0:
            for i in range(self.max_occupancy):
                self.regular_access_semaphore.release()

    def enter_store(self, customer):
        if customer.vip:
            self.semaphore.acquire()
            self.vip_count += 1
            print(f"{get_elapsed_seconds()}s: {customer.name} (Entering)")
        else:
            self.regular_access_semaphore.acquire()
            self.semaphore.acquire()
            print(f"{get_elapsed_seconds()}s: {customer.name} (Entering)")

    def leave(self, customer):
        if customer.vip:
            self.semaphore.release()
            print(f"{get_elapsed_seconds()}s: {customer.name} (Leaving)")

            if self.vip_count == self.number_of_vip:
                for i in range(self.max_occupancy): 
                    self.regular_access_semaphore.release()

        else:
            self.semaphore.release()
            self.regular_access_semaphore.release()
            print(f"{get_elapsed_seconds()}s: {customer.name} (Leaving)")

    def purchase_tickets(self, ticketCount):
        self.earnings_semaphore.acquire()
        self.earnings += self.ticketPrice * ticketCount
        self.earnings_semaphore.release()
        