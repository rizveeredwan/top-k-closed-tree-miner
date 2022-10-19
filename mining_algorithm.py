import heapq

from debug_functions import DebugFunctions
from data_structure import DataStructure, MaxHeap

debug = DebugFunctions()

def generate_bitset_from_nodeids(cspm_tree_nodes):
    # generating bitset from node ids
    # complexity: O(1)
    # https://www.quora.com/Why-is-bit-shifting-regarded-as-an-O-1-operation-and-not-O-n-where-n-is-the-number-of-bits-shifted
    value = 0
    for i in range(len(cspm_tree_nodes)):
        value = value | (1 << cspm_tree_nodes[i])
    return value


class CIET:
    # closted itemset enumeratin tree
    def __init__(self):
        self.cspm_tree_bitset = None
        self.element = None
        self.child = None
        self.support = None
        self.parent = None

    def create(self, parent, edge_label, support): #edge label 1
        node = CIET()
        node.support = support
        node.element = edge_label
        node.parent = parent
        if parent.child is None:
            parent.child = {}
        parent.child[str(edge_label)] = node
        return node


class MiningAlgorithm:
    def __init__(self):
        self.ciet_root = CIET()
        # all the data structure code
        self.ds = DataStructure()
        self.candidate_patterns = []
        heapq.heapify(self.candidate_patterns)


    def find_frequent_itemset(self, cspm_tree_root, K=2):
        # Find frequent 1 itemset
        list_of_items = []
        if cspm_tree_root.down_next_link_ptr is not None:
            for item in cspm_tree_root.down_next_link_ptr:
                # getting the next link nodes node.nl[alpha] = {}
                next_link_nodes, support = cspm_tree_root.get_next_link_nodes(node=cspm_tree_root, item=item)
                # print(cspm_tree_root.node_id, item, next_link_nodes, support)
                # print(f"item = {item}, support = {support}")
                # debug.print_set_of_nodes(nodes=next_link_nodes)
                list_of_items.append([item, support, next_link_nodes])
        self.ciet_root.child = {}
        for i in range(0, len(list_of_items)):
            # edge labels [[a]], [[b]]
            node = self.ciet_root.create(parent=self.ciet_root, edge_label=[[list_of_items[i][0]]],
                                  support=list_of_items[i][1])
            # insert everything in max heap
            heapq.heappush(self.candidate_patterns, MaxHeap(node)) # O(nlogn)
        length = len(self.candidate_patterns)
        while length > 0:
            length -= 1
            u = heapq.heappop(self.candidate_patterns).node
            # condition of the mean heap




