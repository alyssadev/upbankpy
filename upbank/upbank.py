#!/usr/bin/env python3
# TODO: get transaction by ID, get account by ID, webhook functionality
from os import environ
import requests

api = "https://api.up.com.au/api/v1"

class Endpoint:
    endpoint = None
    def __init__(self, endpoint, get=True):
        self.endpoint = endpoint
        if get:
            self.data = self.get()

    def get(self, *args, **kwargs):
        if not self.endpoint:
            raise Exception("endpoint property not set")
        if not kwargs.get("headers"):
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = "Bearer " + environ.get("UP_TOKEN")
        return requests.get(api + self.endpoint, *args, **kwargs).json()

class Webhooks(Endpoint):
    endpoint = "/webhooks"
    def __init__(self):
        self.data = self.get()
        self.webhooks = [Webhook(d) for d in self.data["data"]]
    def __getitem__(self,key):
        return self.webhooks[key]
    def __repr__(self):
        return f"{self.webhooks}"

class Webhook:
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        attributes = data["attributes"]
        self.url = attributes["url"]
        self.createdAt = attributes["createdAt"]
    def __repr__(self):
        return f"<{self.url}>"
    def ping(self):
        kwargs = {}
        if not kwargs.get("headers"):
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = "Bearer " + environ.get("UP_TOKEN")
        return bool(requests.post(api + f"/webhooks/{self.id}/ping", **kwargs))
    def delete(self):
        kwargs = {}
        if not kwargs.get("headers"):
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = "Bearer " + environ.get("UP_TOKEN")
        return bool(requests.delete(api + f"/webhooks/{self.id}", **kwargs))

class Ping(Endpoint):
    endpoint = "/util/ping"
    def __init__(self):
        self.data = self.get()

class Accounts(Endpoint):
    endpoint = "/accounts"
    def __init__(self):
        self.data = self.get()
        self.accounts = [Account(d) for d in self.data["data"]]
    def __getitem__(self,key):
        return self.accounts[key]
    def __repr__(self):
        return f"{self.accounts}"
    def total(self):
        return sum(a.balance.value for a in self.accounts)

class Account:
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.displayName = data["attributes"]["displayName"]
        self.accountType = data["attributes"]["accountType"]
        self.balance = Balance(data["attributes"]["balance"])
        self.createdAt = data["attributes"]["createdAt"]
    def __repr__(self):
        return f"<{self.displayName} ({self.accountType}): {self.balance}>"
    @property
    def transactions(self):
        return Transactions(account=self.id)

class Balance:
    currencyCode = None
    value = None
    valueInBaseUnits = None
    def __init__(self, data):
        self.data = data
        if not data:
            return
        self.currencyCode = data["currencyCode"]
        self.value = float(data["value"])
        self.valueInBaseUnits = data["valueInBaseUnits"]
    def __repr__(self):
        return f"{self.currencyCode}{self.value}"

class Transactions(Endpoint):
    endpoint = "/transactions"
    def __init__(self, account=None, roundUp=False):
        if account:
            endpoint = f"/accounts/{account}/transactions"
        self.data = self.get()
        if roundUp:
            self.transactions = [Transaction(d) for d in self.data["data"]]
        else:
            self.transactions = [Transaction(d) for d in self.data["data"] if d["attributes"]["description"] != "Round Up"]
    def __getitem__(self,key):
        return self.transactions[key]
    def __repr__(self):
        return f"{self.transactions}"
    def total(self):
        return sum(t.amount.value for t in self.transactions)

class Transaction:
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        attributes = data["attributes"]
        self.status = attributes["status"]
        self.rawText = attributes["rawText"]
        self.description = attributes["description"]
        self.message = attributes["message"]
        # TODO: need separate class for HoldInfo and RoundUp?
        if "holdInfo" in attributes and attributes["holdInfo"] is not None:
            self.holdInfo = Balance(attributes["holdInfo"]["amount"])
        if "roundUp" in attributes and attributes["roundUp"] is not None:
            self.roundUp = Balance(attributes["roundUp"]["amount"])
        self.cashback = attributes["cashback"]
        self.amount = Balance(attributes["amount"])
        self.foreignAmount = Balance(attributes["foreignAmount"])
        self.createdAt = attributes["createdAt"] # TODO: create date class
        self.settledAt = attributes["settledAt"]
        # TODO: link to Account object
        self.account = data["relationships"]["account"]["data"]["id"]
    def __repr__(self):
        return f"<{self.description}: {self.amount} {self.createdAt}>"
