from Crypto.Hash import SHA3_256


class MerkleTree:

    def __int__(self):
        self.__merkle_tree_root = None

    @property
    def merkle_tree_root(self):
        return self.__merkle_tree_root

    @merkle_tree_root.setter
    def merkle_tree_root(self, merkle_tree_root):
        self.__merkle_tree_root = merkle_tree_root

    def merkle_tree_check_1(self, transaction_list):
        if len(transaction_list) is 1:
            self.__merkle_tree_root = transaction_list[0]

    def merkle_tree_check_2(self, transaction_list):
        if len(transaction_list) is 2:
            get_elem = str(transaction_list[0] + transaction_list[1])
            h = SHA3_256.new(get_elem.encode())
            self.__merkle_tree_root = h.hexdigest()

    def merkle_tree_construct(self, transaction_list):
        transaction_list_2 = transaction_list.copy()

        self.merkle_tree_check_1(transaction_list=transaction_list_2)
        self.merkle_tree_check_2(transaction_list=transaction_list_2)

        while len(transaction_list_2) > 0:
            if len(transaction_list_2) % 2 is not 0:
                transaction_list_2.append(transaction_list_2[len(transaction_list_2) - 1])
            if len(transaction_list_2) is 1:
                break
            position1 = 0
            position2 = 1
            if position1 is len(transaction_list_2) - 2 and position2 is len(transaction_list_2) - 1:
                break
            x = transaction_list_2[position1]
            y = transaction_list_2[position2]
            transaction_list_2.remove(x)
            transaction_list_2.remove(y)
            get_elem = str(x + y)
            h = SHA3_256.new(get_elem.encode())
            transaction_list_2[position1] = h.hexdigest()
            position1 += 2
            position2 += 2

        self.merkle_tree_check_1(transaction_list=transaction_list_2)
        self.merkle_tree_check_2(transaction_list=transaction_list_2)

        return self.__merkle_tree_root
