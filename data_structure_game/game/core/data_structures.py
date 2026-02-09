from __future__ import annotations
from typing import Any, Optional, List, Dict, Tuple
from enum import Enum
import random

class OperationType(Enum):
    PUSH = "push"
    POP = "pop"
    ENQUEUE = "enqueue"
    DEQUEUE = "dequeue"
    INSERT = "insert"
    DELETE = "delete"
    SEARCH = "search"
    TRAVERSE = "traverse"

class DataStructure:
    def __init__(self, name: str):
        self.name = name
        self.elements: List[Any] = []
        self.operations: List[Tuple[OperationType, Any]] = []
    
    def get_state(self) -> Dict:
        return {
            'elements': self.elements.copy(),
            'operations': self.operations.copy()
        }
    
    def reset(self):
        self.elements.clear()
        self.operations.clear()

class Stack(DataStructure):
    def __init__(self):
        super().__init__("Stack")
    
    def push(self, item: Any) -> bool:
        self.elements.append(item)
        self.operations.append((OperationType.PUSH, item))
        return True
    
    def pop(self) -> Any:
        if not self.elements:
            return None
        item = self.elements.pop()
        self.operations.append((OperationType.POP, item))
        return item
    
    def peek(self) -> Any:
        return self.elements[-1] if self.elements else None

class Queue(DataStructure):
    def __init__(self):
        super().__init__("Queue")
    
    def enqueue(self, item: Any) -> bool:
        self.elements.append(item)
        self.operations.append((OperationType.ENQUEUE, item))
        return True
    
    def dequeue(self) -> Any:
        if not self.elements:
            return None
        item = self.elements.pop(0)
        self.operations.append((OperationType.DEQUEUE, item))
        return item

class LinkedListNode:
    def __init__(self, value: Any):
        self.value = value
        self.next: Optional[LinkedListNode] = None

class LinkedList(DataStructure):
    def __init__(self):
        super().__init__("Linked List")
        self.head: Optional[LinkedListNode] = None
        self.elements = []  # For compatibility with base class
    
    def insert(self, value: Any, position: int = 0) -> bool:
        new_node = LinkedListNode(value)
        
        if position == 0 or not self.head:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            for _ in range(position - 1):
                if not current.next:
                    break
                current = current.next
            new_node.next = current.next
            current.next = new_node
        
        self._update_elements()
        self.operations.append((OperationType.INSERT, (value, position)))
        return True
    
    def delete(self, value: Any) -> bool:
        if not self.head:
            return False
            
        if self.head.value == value:
            self.head = self.head.next
            self._update_elements()
            self.operations.append((OperationType.DELETE, value))
            return True
            
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self._update_elements()
                self.operations.append((OperationType.DELETE, value))
                return True
            current = current.next
            
        return False
    
    def _update_elements(self):
        self.elements = []
        current = self.head
        while current:
            self.elements.append(current.value)
            current = current.next

class BinaryTreeNode:
    def __init__(self, value: Any):
        self.value = value
        self.left: Optional[BinaryTreeNode] = None
        self.right: Optional[BinaryTreeNode] = None

class BinaryTree(DataStructure):
    def __init__(self):
        super().__init__("Binary Tree")
        self.root: Optional[BinaryTreeNode] = None
    
    def insert(self, value: Any) -> bool:
        if not self.root:
            self.root = BinaryTreeNode(value)
            self._update_elements()
            self.operations.append((OperationType.INSERT, value))
            return True
            
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            
            if not node.left:
                node.left = BinaryTreeNode(value)
                self._update_elements()
                self.operations.append((OperationType.INSERT, value))
                return True
            else:
                queue.append(node.left)
                
            if not node.right:
                node.right = BinaryTreeNode(value)
                self._update_elements()
                self.operations.append((OperationType.INSERT, value))
                return True
            else:
                queue.append(node.right)
        
        return False
    
    def _update_elements(self):
        self.elements = []
        if not self.root:
            return
            
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            if node:
                self.elements.append(node.value)
                queue.append(node.left)
                queue.append(node.right)
            else:
                self.elements.append(None)

class Graph(DataStructure):
    def __init__(self):
        super().__init__("Graph")
        self.adjacency_list: Dict[Any, List[Any]] = {}
    
    def add_vertex(self, vertex: Any) -> bool:
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
            self._update_elements()
            return True
        return False
    
    def add_edge(self, vertex1: Any, vertex2: Any) -> bool:
        if vertex1 in self.adjacency_list and vertex2 in self.adjacency_list:
            if vertex2 not in self.adjacency_list[vertex1]:
                self.adjacency_list[vertex1].append(vertex2)
                self.adjacency_list[vertex2].append(vertex1)  # For undirected graph
                self._update_elements()
                self.operations.append((OperationType.INSERT, (vertex1, vertex2)))
                return True
        return False
    
    def _update_elements(self):
        self.elements = []
        for vertex, neighbors in self.adjacency_list.items():
            self.elements.append((vertex, neighbors))
    
    def bfs(self, start_vertex: Any) -> List[Any]:
        visited = []
        queue = [start_vertex]
        
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.append(vertex)
                queue.extend([v for v in self.adjacency_list[vertex] if v not in visited])
        
        self.operations.append((OperationType.TRAVERSE, ("BFS", start_vertex)))
        return visited
