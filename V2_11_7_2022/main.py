import functools
import os
import sys
from timeit import default_timer as timer

import debug_functions
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

    def print_final_closed_patterns(self):
        ct = 0
        all_patterns = []
        for key in self.mine.support_table:
            print(f"support = {key}")
            """
            # trie version 
            val, _list = self.mine.support_table[key].closed_patterns_with_trie[0].print_patterns(type=0)
            """
            # linked list version
            val, _list = self.mine.support_table[key].closed_patterns.print()
            ct += (val-1)
            for i in range(0, len(_list)):
                all_patterns.append((key, str(_list[i][0])))
        all_patterns.sort(key=functools.cmp_to_key(debug_functions.pattern_sort_func))
        f = open(os.path.join('kclotreeminer_output.txt'), 'w')
        for i in range(0, len(all_patterns)):
            print(all_patterns[i][0], all_patterns[i][1])
            f.write(str(all_patterns[i][0])+'\n')
            f.write(str(all_patterns[i][1])+'\n')
        # f.write(str(ct)+'\n')
        print("total patterns ",ct)

    def clo_tree_miner(self, K):
        NODE_MAPPER = return_node_mapper()
        start = timer()
        self.mine.k_clo_tree_miner(cspm_tree_root=self.cspm_tree_root, K=K, NODE_MAPPER=NODE_MAPPER)
        end = timer()
        print("Algorithm Done")
        # self.print_closed_patterns()
        self.print_final_closed_patterns()
        print(f"{end - start}")


if __name__ == '__main__':
    obj = Main()
    obj.read(file_name=os.path.join('.', 'dataset', 'closed_dataset15.txt'))
    obj.clo_tree_miner(K=23)
