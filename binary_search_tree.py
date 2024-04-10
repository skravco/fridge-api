class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def _insert_recursive(self, data, node):
        if data["id"] < node.data["id"]:
            if node.left is None:
                node.left = Node(data)
            else:
                self._insert_recursive(data, node.left)
        elif data["id"] > node.data["id"]:
            if node.right is None:
                node.right = Node(data)
            else:
                self._insert_recursive(data, node.right)
        else:
            return

    def insert(self, data):
        if self.root is None:
            self.root = Node(data)
        else:
            self._insert_recursive(data, self.root)

    def _search_recursive(self, recipe_id, node):

        if recipe_id == node.data["id"]:
            return node.data

        if recipe_id < node.data["id"] and node.left is not None:
            return self._search_recursive(recipe_id, node.left)

        if recipe_id > node.data["id"] and node.right is not None:
            return self._search_recursive(recipe_id, node.right)

        return False

    def search(self, recipe_id):
        recipe_id = int(recipe_id)
        if self.root is None:
            return False

        return self._search_recursive(recipe_id, self.root)
