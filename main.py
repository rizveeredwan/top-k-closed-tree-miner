import os

from cspm_tree import CSPMTree, global_node_count, return_node_mapper
from database import Database
from debug_functions import DebugFunctions
from mining_algorithm import KCloTreeMiner

"""
# Extension Convention 
0: Sequence extension (SE)
1: Itemset extension (IE)  
"""


class Main:
    def __init__(self):
        self.cspm_tree_root = CSPMTree()
        self.debug = DebugFunctions()
        self.mine = KCloTreeMiner()

    def read(self, file_name):
        database_object = Database()
        database_object.ReadFile(file_name)
        # database_object.PrintDatabase() # Printing raw database
        successors = {}
        item_freq = {}
        ct = 0
        for key in database_object.insert_database:
            ct += 1
            print(key, database_object.insert_database[key])
            # print(self.cspm_tree_root)
            # insertion into the tree
            self.cspm_tree_root.insert(sp_tree_node=self.cspm_tree_root,
                                       processed_sequence=database_object.insert_database[key], event_no=0, item_no=0,
                                       event_bitset=0)
            print(global_node_count)
        self.cspm_tree_root.nextlink_gen_using_dfs(self.cspm_tree_root)
        # debug
        # self.debug.sanity_test_next_links(self.cspm_tree_root)

    def print_closed_patterns(self):
        for key in self.mine.support_table:
            print(f"support = {key}")
            self.mine.support_table[key].closed_patterns.print()

    def clo_tree_miner(self, K):
        NODE_MAPPER = return_node_mapper()
        self.mine.k_clo_tree_miner(cspm_tree_root=self.cspm_tree_root, K=K, NODE_MAPPER=NODE_MAPPER)
        self.print_closed_patterns()
        print("\n")
        # print(NODE_MAPPER)


if __name__ == '__main__':
    obj = Main()
    obj.read(file_name=os.path.join('.', 'dataset', 'closed_dataset1.txt'))
    obj.clo_tree_miner(K=4)

