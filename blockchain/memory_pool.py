from utility import Utility

MINIMUM_MINING_FEE = 0.5
MINIMUM_RELAY_FEE = 0.5
THRESHOLD_SIZE = 0.5


class Mempool:

    def __init__(self):
        self.__mempool = []

    @property
    def mempool(self):
        return self.__mempool[:]

    @mempool.setter
    def mempool(self, mempool):
        self.__mempool = mempool

    def fee_based_mempool(self, incoming_transactions):
        first_array = []
        for i in range(0, len(incoming_transactions)):
            if Utility.check_address_format(incoming_transactions[i]['recipient']):
                if incoming_transactions[i]['relay_fees'] > MINIMUM_RELAY_FEE:
                    first_array.append(incoming_transactions[i])

        if len(first_array) > THRESHOLD_SIZE:
            for i in range(0, len(first_array)):
                if Utility.check_address_format(first_array[i]['recipient']):
                    if first_array[i]['fees'] > MINIMUM_MINING_FEE:
                        self.__mempool.append(first_array[i])

        return self.__mempool[:]

# obj = Mempool()

# incom_transactions = [
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIA',
# 'recipient': 'DM0hPXsFAsAKUyo8b6MgtknBFKiidCQbFMt3QyfDThNK8', 'fees': 0.5, 'relay_fees': 0.4},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIC',
# 'recipient': 'DMLpw++9HwIm8vQ9wNe4e+bfJlyuKcud4ta40ufcv7CuY', 'fees': 0.3, 'relay_fees': 0.45},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUID',
# 'recipient': 'DMCW4FLdFcmePCsU9ai/xuoPMbiJ30zjQEEHFI5sZGuRk', 'fees': 0.65, 'relay_fees': 0.7},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIE',
# 'recipient': 'DMFtUS+EMPUyKDhOR2fc3G8SCHsL1yleGKPT2V1luogTM', 'fees': 0.55, 'relay_fees': 0.35},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIF',
# 'recipient': 'DMJPTIXE792RpsoeVYwu3GTuzz+74y4Vs1GiuX1oxrXFc', 'fees': 0.8, 'relay_fees': 0.9},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIG',
# 'recipient': 'DMIjlooxiGawO75tRqrI9BpwVOS4/gjnslZDw+cFkT4oM', 'fees': 0.7, 'relay_fees': 0.2},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIH',
# 'recipient': 'DMgVB5/9whOl3Vuxaf6ShoCa+PBJ/3Ij6hKeAS/pB7EY8', 'fees': 0.2, 'relay_fees': 0.95},
# {'sender': 'DMrCqlBJIcWz8jx54YUN1wTIe+dscBVwYDekGqMbjeUIJ',
# 'recipient': 'DM4Ta08ddn8M0Ze1+LNRIIJO18BIksCO4je48B6chKZZU', 'fees': 0.7, 'relay_fees': 0.2}
# ]

# print(obj.fee_based_mempool(incom_transactions))
