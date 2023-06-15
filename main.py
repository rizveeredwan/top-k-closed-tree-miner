import functools
import os
import sys
import time
from timeit import default_timer as timer
import tracemalloc
import psutil

import debug_functions
from cspm_tree import CSPMTree, global_node_count, return_node_mapper, set_node_mapper_flag
from database import Database
from closed_mining import KCloTreeMiner

from maximal_pattern_find import *
from closed_mining import *
from clustering import *

"""
# Extension Convention
0: Sequence extension (SE)
1: Itemset extension (IE)
"""


class Main:
    def __init__(self, HOOK_BITSET_BASED_NODE_PROJECTION=None):
        self.cspm_tree_root = CSPMTree()
        self.mine = KCloTreeMiner()
        set_node_mapper_flag(HOOK_BITSET_BASED_NODE_PROJECTION)

    def read(self, file_name):
        database_object = Database()
        database_object.ReadFile(file_name, operation_flag_on=False)
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

    def apply_summarizaion(self, mined_closed_patterns, clustering_type="k_means", K=3,
                           max_number_of_iterations=1000, cspm_root=None, tolerance=50):
        # example, mined_closed_patterns = {3: [a, b, c], 2: [d, dc] ... }
        if clustering_type == "k_means" or clustering_type == "k_medoid":
            group_of_patterns = []
            for support in mined_closed_patterns:
                for i in range(0, len(mined_closed_patterns[support])):
                    group_of_patterns.append(mined_closed_patterns[support][i])
            assert (cspm_root is not None)
            if clustering_type == "k_means":
                entities = k_centroid_clustering(group_of_patterns=group_of_patterns, K=K,
                                                 max_number_of_iterations=max_number_of_iterations,
                                                 cspm_root=cspm_root,
                                                 tolerance=tolerance)
            if clustering_type == "k_medoid":
                entities = k_medoids_clustering(group_of_patterns=group_of_patterns, K=K,
                                                max_number_of_iterations=max_number_of_iterations, cspm_root=cspm_root,
                                                tolerance=tolerance)
            print_cluster_stat(entities=entities, group_of_patterns=group_of_patterns, cspm_root=cspm_root,
                               intra_dist_flag=True, inter_dist_flag=True, silhouette_flag=True, pattern_normalize_flag=True)


        else:
            if clustering_type == "max_woc":
                set_of_maximal_pattern = {}
                for support in mined_closed_patterns:
                    set_of_maximal_pattern[support] = [calculate_maximal_pattern_light_constraint(pattern_cluster=
                                                                                                  mined_closed_patterns[
                                                                                                      support])]
            if clustering_type == "max_wc":
                set_of_maximal_pattern = calculate_maximal_pattern_hard_constraint_greedy(mined_closed_patterns,
                                                                                          self.cspm_tree_root)
            print_set_of_maximal_pattern(set_of_maximal_pattern, mined_closed_patterns, normalized=True)
        """
        f = open(os.path.join('kclotreeminer_output.txt'), 'w')
        for i in range(0, len(all_patterns)):
            print(all_patterns[i][0], all_patterns[i][1])
            f.write(str(all_patterns[i][0])+'\n')
            f.write(str(all_patterns[i][1])+'\n')
        # f.write(str(ct)+'\n')
        print("total patterns ",ct)
        """

    def clo_tree_miner(self, K, mining_type="generic", summarize_flag=False, clusterting_type="k_means",
                       max_number_of_iterations=100, tolerance=50):
        # mining_type = "generic", "group", "unique"
        NODE_MAPPER = return_node_mapper()
        start = timer()
        mined_closed_patterns = self.mine.k_clo_tree_miner(cspm_tree_root=self.cspm_tree_root, K=K,
                                                           NODE_MAPPER=NODE_MAPPER,
                                                           mining_type=mining_type)
        if mining_type == "group" and summarize_flag is True:
            self.apply_summarizaion(mined_closed_patterns, K=K, max_number_of_iterations=max_number_of_iterations,
                                    cspm_root=self.cspm_tree_root,
                                    tolerance=tolerance, clustering_type=clusterting_type)
        end = timer()
        print("Algorithm Done")
        print(f"{mined_closed_patterns}")
        # self.print_closed_patterns()
        # self.print_final_closed_patterns()
        # print(f"{end - start}")


if __name__ == '__main__':
    # starting the monitoring
    start_time = time.process_time()
    tracemalloc.start()
    obj = Main(HOOK_BITSET_BASED_NODE_PROJECTION=True)
    obj.read(file_name=os.path.join('.', 'dataset', 'msnbc.txt'))
    obj.clo_tree_miner(K=100, mining_type="group", summarize_flag=True, clusterting_type="k_medoid",
                       max_number_of_iterations=200, tolerance=70)
    # displaying the memory
    current, peak = tracemalloc.get_traced_memory()
    print(f"current = {current / 1024.0} Kib and peak = {peak / 1024.0} Kib")
    # stopping the library
    tracemalloc.stop()
    end_time = time.process_time()
    print(f"total elapsed time {end_time-start_time}")

