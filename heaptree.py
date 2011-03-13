#!/usr/bin/python

import operator
from collections import deque

class HeapNode(object):
    """Class to represent a node in a HeapTree.

        value = the object stored in this node.
        left = the left sub-tree of this node.
        right = the right sub-tree of this node.
        parent = the parent node of this node.
    """
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

    def _swapchild(self, other, hand):
        """Swaps the children of self with those of other.
        """
        otherchild = getattr(other, hand)
        selfchild = getattr(self, hand)
        # Swap the children.
        setattr(other, hand, selfchild)
        setattr(self, hand, otherchild)
        # Set the child nodes' parents.
        if otherchild:
            otherchild.parent = self
        if selfchild:
            selfchild.parent = other

    def _getparenthand(self):
        """Finds which attribute of its parent node self is attached to.

        Returns:
            a string representing the name of the parent node's attribute, or
            None, if self has no parent (should be the root node).
        """
        if self.parent is None:
            return None
        for hand in ('left', 'right'):
            if getattr(self.parent, hand) is self:
                return hand
        else:
            raise StandardException("node's parent is not connected to node")

    def _changeparentnode(self, other):
        """Changes the parent node of self to point to other.
        """
        hand = self._getparenthand()
        if hand is None:
            return
        setattr(self.parent, hand, other)

    def _swapparent(self, other):
        """Swaps the parents of the self and other nodes.
        """
        selfparent = self.parent
        otherparent = other.parent
        # Swap the parents.
        self.parent = otherparent
        other.parent = selfparent
        # Change each node's parent node to point to the other.
        self._changeparentnode(other)
        other._changeparentnode(self)

    def swap(self, other):
        self._swapchild(other, "left")
        self._swapchild(other, "right")
        self._swapparent(other)


class HeapTree(object):
    """Class to represent a Binary Heap as a tree.
    """
    def __init__(self, cmp=operator.le):
        """Create an empty Heap.

        Args:
            cmp: comparison operator used to define the heap.
        """
        self.root = None
        self._size = 0
        self.cmp = cmp

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        """Gets the node at the specified inorder index.

        Inorder index means index of a node, if the heap was represented as an
        array, where the children of node i are [2i + 1] and [2i + 2].
        The root node is index 0.

        Args:
            index: the 

        Raises:
            IndexError: no node exists at the requested index.
        """
        path = bin(index + 1)[2:]
        node = self.root
        for c in path[1:]:
            if node is None:
                raise IndexError
            if c == '0':
                node = node.left
            elif c == '1':
                node = node.right
            else:
                assert False, "bin string %s has non-binary character " % path
        if node is None:
            raise IndexError
        return node

    def add(self, value):
        """Add a value to the heap.
        """
        newnode = HeapNode(value)
        if self.root is None:
            self.root = newnode
        else:
            # To do this, we need to get the parent of that node.
            # The parent of node [i] is at index [(i-1) >> 1].
            parent = self[(len(self) - 1) >> 1]
            if parent.left is None:
                parent.left = newnode
            else:
                assert parent.right is None
                parent.right = newnode
            newnode.parent = parent
            self._bubbleup(newnode)
        self._size += 1
        return newnode

    def _bubbleup(self, node):
        """Move the given node up the near-heap until it satisfies the heap
        property.

        Used when the value of a node changes

        Args:
            node: (HeapNode) node to move within the heap.
        """
        if node is not self.root:
            if self.cmp(node.value, node.parent.value):
                self._swapnodewithparent(node)
                self._bubbleup(node)

    def _bubbledown(self, node):
        """Move the given node down the heap until the heap property is
        satisfied.

        Used when the value of a node changes

        Args:
            node: (HeapNode) node to move within the heap.
        """
        left = node.left
        right = node.right
        largest = node
        if left is not None and self.cmp(left.value, node.value):
            largest = left
        if right is not None and self.cmp(right.value, largest.value):
            largest = right
        if largest is not node:
            self._swapnodewithparent(largest)
            self._bubbledown(node)

    def _swapnodewithparent(self, node):
        """Swap a node with its parent.
        """
        assert node is not self.root
        parent = node.parent
        if parent is self.root:
            self.root = node
            node.parent = None
        else:
            # Attach the node to its new parent (i.e. its old grandparent)
            grandparent = parent.parent
            node.parent = grandparent
            if grandparent.left is parent:
                grandparent.left = node
            else:
                assert grandparent.right is parent
                grandparent.right = node
        # Save the node's old children to attach them to the parent later.
        left = node.left
        right = node.right
        # Swap parent and node, attach the parent's other child to node.
        parent.parent = node
        if parent.left is node:
            node.left = parent
            node.right = parent.right
            if node.right is not None:
                assert node.right.parent is parent
                node.right.parent = node
        else:
            assert parent.right is node
            node.right = parent
            node.left = parent.left
            if node.left is not None:
                assert node.left.parent is parent
                node.left.parent = node
        # Make node's old children the old parent's children
        parent.left = left
        if left is not None:
            assert left.parent is node
            left.parent = parent
        parent.right = right
        if right is not None:
            assert right.parent is node
            right.parent = parent

    def deleteroot(self):
        """Remove and return the root node from the heap.

        Returns:
            the root node.

        Raises:
            IndexError: if the heap is empty.
        """
        # Get the last inorder node in the tree.
        root = self.root
        if len(self) == 0:
            raise IndexError("Heap is empty")
        elif len(self) == 1:
            self.root = None
        else:
            lastnode = self[len(self) - 1]
            self._replaceroot(lastnode)
            self._bubbledown(lastnode)
        self._size -= 1
        return root

    def _replaceroot(self, node):
        """Makes node the root node.
        Used in deleteroot.
        """
        # Detatch the node from its parent.
        if node.parent.left is node:
            node.parent.left = None
        else:
            assert node.parent.right is node
            node.parent.right = None
        # Copy the root's relations to the replacement node.
        node.parent = None
        node.left = self.root.left
        if node.left is not None:
            node.left.parent = node
        node.right = self.root.right
        if node.right is not None:
            node.right.parent = node
        # Clear the old root's relations.
        self.root.left = None
        self.root.right = None
        # Replace self.root
        self.root = node

    def _heapify(self, node):
        self._bubbleup(node)
        self._bubbledown(node)

    def to_list(self):
        """Returns a copy of the HeapTree as a list.

        Return:
            a list representing the same Heap as self.
        """
        if self.root is None:
            return []
        a = []
        q = deque([self.root])
        while len(q) > 0:
            head = q.popleft()
            a.append(head.value)
            if head.left:
                q.append(head.left)
            if head.right:
                q.append(head.right)
        return a

