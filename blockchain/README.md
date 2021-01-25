## Blockchain App (DMcoin)

## Features

- Block structure is similar to the structure of other cryptocurrencies
- PoW-based consensus mechanism
- scrypt with SHA3 as PoW function
- Deterministic ECC wallet based on password key derivation (PBKDF2)
- Longest chain rule
- Filter mechanism for memory pool design
- Round-robin random number generator mechanism for eclipse attacks
- P2P network based on HTTP endpoints
- Flask framework on the server side
- Vue.js framework on the client side
- The development of the app has been done with [PyCharm IDE](https://www.jetbrains.com/pycharm/)

## How to run the app

```bash
python web_node.py -p 5001
```

A first server will run on port 5001.


```bash
python web_node -p 5002
```

A second server will run on port 5002. You can continue in this manner and run more servers.