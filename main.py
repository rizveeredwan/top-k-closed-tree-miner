import os

from cspm_tree import CSPMTree, global_node_count
from database import Database
from debug_functions import DebugFunctions


class Main:
    def __init__(self):
        self.cspm_tree_root = CSPMTree()
        self.debug = DebugFunctions()

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
            successors.clear()
            self.cspm_tree_root.insert(sp_tree_node=self.cspm_tree_root, processed_sequence=database_object.insert_database[key],
                                       event_no=0, item_no=0, successors=successors, seq_sum=None, event_bitset=0)
            print(global_node_count)
        # debug
        self.debug.sanity_test_next_links(self.cspm_tree_root)


        # saving the node from where the present_count is transferred to previous_count
        """
        for key in database_object.insert_database:
            print(key,database_object.insert_database[key])

            # debug
            # self.debug_functions.InsertIntoDebugDatabase(key,self.debug_database, database_object.insert_database[key])

            node = self.root
            actual_event_no = -1
            addition_type = True # Insert
            if(self.seq_sum.get(key) == None): # Insert
                self.seq_sum[key] = SequenceSummarizerStructure()
                self.seq_sum[key].node_upto_mined = self.root # null node basically
                self.seq_sum[key].sp_tree_end_node_ptr_prev = self.root # initial ending node reference
            else:
                node = self.seq_sum[key].sp_tree_end_node_ptr
                actual_event_no = node.event_no
                addition_type = False # Append
                self.seq_sum[key].sp_tree_end_node_ptr_prev = self.seq_sum[key].sp_tree_end_node_ptr # updating with previous end

            new_items.clear()
            item_freq.clear()
            next_link_nodes.clear()
            modified_next_link_nodes.clear()
            end_node = self.psptree_function.Insert(pass_no, node, database_object.insert_database[key], 0, 0, actual_event_no, 0, new_items, self.seq_sum[key])
            update_modified_information.clear()
            previous_count_transferred.clear()
            self.psptree_function.UpdatingNodeAttributes(end_node, self.last_mined_pass_no, pass_no, addition_type, node, False, item_freq, next_link_nodes, modified_next_link_nodes, update_modified_information, previous_count_transferred)

            # update sequence summarizer
            self.seq_sum[key].UpdateCETables(new_items, self.cetables, self.seq_sum[key], actual_event_no)
            self.seq_sum[key].UpdateCETablei(new_items, self.cetablei, self.seq_sum[key])
            self.seq_sum[key].sp_tree_end_node_ptr = end_node

            # debug
            self.Debug_InsertInAffectedDatabase(key,database_object.insert_database[key])

        # self.debug_functions.Debug_SanityCheck(self.root)
        deleted_nodes,affected_patterns_ptr,affected_patterns_trie_root="","",""

        for key in database_object.delete_database:
            print(key,database_object.delete_database[key])
            # last node of the sequence
            node = self.seq_sum[key].sp_tree_end_node_ptr
            node_mapper.clear()
            path_existing_modification_info_old.clear()  # clearing previous information
            deleted_nodes, affected_patterns_ptr, deleted_items, prev_end_node_ptr_idx = self.psptree_function.FindingDeletedNodes(database_object.delete_database[key] ,self.root, self.seq_sum[key].node_upto_mined.event_no, node_mapper, self.seq_sum[key], path_existing_modification_info_old, self.last_mined_pass_no)
            print(len(deleted_nodes), len(affected_patterns_ptr))
            affected_patterns_trie_root = self.psptree_function.PatternTrieMaker(affected_patterns_ptr) # getting the affected pattern's trie root
            # finding the shift nodes
            update_modified_information.clear()
            shift_nodes, status_shift_nodes, prev_end_node_ptr_idx = self.psptree_function.FindingShiftNodes(self.seq_sum[key].sp_tree_end_node_ptr , deleted_nodes[len(deleted_nodes)-1], self.seq_sum[key].node_upto_mined.event_no ,node_mapper, self.seq_sum[key].sp_tree_end_node_ptr_prev, deleted_nodes, prev_end_node_ptr_idx,  update_modified_information, self.last_mined_pass_no)
            # removing the complete set of unnecessary unmodified nodes
            ModifiedAttributeCalculations.RemovingUnnecessaryModifiedNodes_Merge(path_existing_modification_info_old, update_modified_information)


            assert(prev_end_node_ptr_idx != None and prev_end_node_ptr_idx >= -1) # it can not be none or (-1 or some other values)
            print(len(shift_nodes),len(status_shift_nodes))
            # finding the nodes of the new path
            path_existing_modification_info_new.clear()
            new_path_nodes, status_new_path_nodes, number_of_overlapped_nodes = self.psptree_function.FindingTheNodesofNewPath( deleted_nodes, shift_nodes, status_shift_nodes, self.root, len(database_object.delete_database[key]), pass_no, node_mapper, self.seq_sum[key], path_existing_modification_info_new, self.last_mined_pass_no)
            print(len(new_path_nodes),len(status_new_path_nodes), "number of overlapped nodes = ",number_of_overlapped_nodes)
            print(node_mapper)
            # updating two paths paralelly
            self.psptree_function.ParallelPathUpdate(number_of_overlapped_nodes, deleted_nodes, shift_nodes, status_shift_nodes, new_path_nodes, status_new_path_nodes,
                        self.last_mined_pass_no, pass_no,self.seq_sum[key].node_upto_mined.event_no,self.seq_sum[key].sp_tree_end_node_ptr.event_no, len(database_object.delete_database[key]), self.root, node_mapper,prev_end_node_ptr_idx)

            remove_item =  SequenceSummarizerCalculationFunctions.CETablesCalculation(deleted_items,self.seq_sum[key],self.cetables)
            SequenceSummarizerCalculationFunctions.CETableiCalculation(deleted_items,self.seq_sum[key],self.cetablei)
            SequenceSummarizerCalculationFunctions.RemoveEntryFromSequenceSummarizer(self.seq_sum[key],remove_item)

            # debug
            # self.debug_functions.Debug_CooccurrenceInforamtion(self.debug_database[key],database_object.delete_database[key],self.seq_sum[key])


            if(len(new_path_nodes)>0):
                self.seq_sum[key].sp_tree_end_node_ptr = new_path_nodes[len(new_path_nodes)-1]
                self.UpdateEndNodePtr(self.seq_sum[key], deleted_nodes, shift_nodes, new_path_nodes,prev_end_node_ptr_idx)
            else:
                del self.seq_sum[key] # this sequence is deleted
            del shift_nodes,status_shift_nodes,new_path_nodes,status_new_path_nodes,deleted_nodes
            # debug
            self.Debug_DeletionInAffectedDatabase(key,database_object.delete_database[key])

        # debug
        # self.psptree_function.DebugPrintNextLink(main.root)
        self.debug_functions.Debug_SanityCheck(self.root,self.last_mined_pass_no)
        self.debug_functions.Debug_ModifiedAtChecking(self.debug_affected_database, self.root, self.last_mined_pass_no)
        """


if __name__ == '__main__':
    obj = Main()
    obj.read(file_name=os.path.join('.', 'dataset', 'next_link_test_dataset2.txt'))

