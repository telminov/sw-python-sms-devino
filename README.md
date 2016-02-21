# sw-python-sms-devino
[![Build Status](https://travis-ci.org/telminov/sw-python-sms-devino.svg?branch=master)](https://travis-ci.org/telminov/sw-python-sms-devino)
[![Coverage Status](https://coveralls.io/repos/github/telminov/sw-python-sms-devino/badge.svg?branch=master)](https://coveralls.io/github/telminov/sw-python-sms-devino?branch=master)

Integration with API of [devinotele.com](http://devinotele.com/)

## Install
```
pip install sw-python-sms-devino
```

## Usage
```python
from sms_devino.client import DevinoClient

client = DevinoClient('tester', '123')
client.get_balance()

result = client.send_one(
    'MyCompany', '89161234567',
    'test message'
)
print(result.sms_ids)

results = client.send_bulk(
    'MyCompany', ['89161234567', '89167654321'],
    test message'
)
print('Total messages:', len(results))
for result in results:
    print(result.sms_ids)

state = client.get_state('123123123213')
print('code\t\t', state.code)
print('description\t', state.description)
print('price\t\t', state.price)
print('creation_dt\t', state.creation_dt)
print('submitted_dt\t', state.submitted_dt)
print('reported_dt\t', state.reported_dt)
print('result_dt\t', state.result_dt)

```
