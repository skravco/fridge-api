class Node:
    def __init__(self, data, next):
        self.data = data
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def to_list(self):
        l = []
        if self.head is None:
            return l

        node = self.head
        while node:
            l.append(node.data)
            node = node.next
        return l

    def print_ll(self):
        ll_string = ""
        node = self.head

        if node is None:
            print(None)

        while node:
            ll_string += f" {str(node.data)} -> "
            node = node.next

        ll_string += "None"
        print(ll_string)

    def insert_head(self, data):
        if self.head is None:
            self.head = Node(data, None)
            self.tail = self.head
            return

        new = Node(data, self.head)
        self.head = new

    def insert_tail(self, data):
        if self.head is None:
            self.insert_head(data)
            return
        self.tail.next = Node(data, None)
        self.tail = self.tail.next

    def get_single_node(self, cuisine_id):
        node = self.head
        while node:
            if node.data["id"] is int(cuisine_id):
                return node.data
            node = node.next
        return None
