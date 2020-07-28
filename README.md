upbankpy
========

A Python wrapper for the newly released API for up.com.au

Usage
-----

Set the environment variable UP\_TOKEN with your personal access token from https://developer.up.com.au/

```python
>>> import upbank
>>> accounts = upbank.Accounts()
>>> print(accounts)
<[<Up Account (TRANSACTIONAL): AUD1>, <Savings (SAVER): AUD1>]>
>>> transactions = accounts[0].transactions
>>> print(transactions[0])
<Merchant: AUD-10.55 2020-07-27T22:37:26+10:00>
```
