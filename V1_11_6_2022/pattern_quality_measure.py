from data_structure import generate_cspm_tree_nodes_from_bitset, CandidatePatternLinkedListNode
from debug_functions import *

def event_enclose_check(event_A, event_B):
    # will check if event_A encloses event_B
    j = 0
    for i in range(0, len(event_B)):
        found = False
        while j < len(event_A):
            if event_B[i] == event_A[j]:
                j += 1
                found = True  # item found
                break
            elif event_B[i] < event_A[j]:  # A's item is bigger, can't hold B[i]
                break
            elif event_B[i] > event_A[j]:  # still a big item in A can be found
                j += 1
                continue
        if found is False:
            return False
    return True  # encloses


def two_pattern_enclose_check(A, B):
    # will check if full pattern A encloses full pattern B
    if len(B) > len(A):  # B is huge, A can never include B
        return False
    event_A, event_B = 0, 0
    while event_B < len(B):
        if event_A == len(A):
            return False  # all the events have been checked, not encloses
        verdict = event_enclose_check(event_A=A[event_A], event_B=B[event_B])
        if verdict is True:
            event_B += 1
        event_A += 1  # next event shift
    if event_B == len(B):
        return True  # A completely encloses B
    return False


def same_subtree_checking(pattern_node, super_pattern_node):
    base_parent_code = pattern_node.subtree_detection_code[0:len(pattern_node.subtree_detection_code)-pattern_node.depth+1]
    base_super_pattern_code = super_pattern_node.subtree_detection_code[0:len(super_pattern_node.subtree_detection_code)-super_pattern_node.depth+1]
    if base_parent_code == "":
        base_parent_code = "-1"
    if base_super_pattern_code == "":
        base_super_pattern_code = "-1"
    if int(base_super_pattern_code) < int(base_parent_code):
        return -1 # small
    if int(base_super_pattern_code) > int(base_parent_code):
        return 1 # big
    pattern_code = pattern_node.subtree_detection_code[len(pattern_node.subtree_detection_code)-pattern_node.depth+1:]
    super_pattern_code = super_pattern_node.subtree_detection_code[len(super_pattern_node.subtree_detection_code)-super_pattern_node.depth+1:]

    # if supper_pattern_node and pattern_node are in the same subtree or not
    i, j = 0, 0
    while i < len(pattern_code) and j < len(super_pattern_code):
        if i < len(pattern_code) and j < len(super_pattern_code):
            if pattern_code[i] == super_pattern_code[j]:
                i += 1
                j += 1
                continue
            elif pattern_code[i] > super_pattern_code[j]:
                return -1
            elif pattern_code[i] < super_pattern_code[j]:
                return 1
        else:
            if j < len(super_pattern_code) and i >= len(pattern_code):
                return 1
            if j >= len(super_pattern_code) and i < len(pattern_code):
                return -1
            pass
    return 0  # perfectly matched


def two_pattern_absorption_check(nodes_of_A, nodes_of_B):
    # A has enclosed B
    # decision if it is enough to keep A only
    # same subtree, same event number
    # print_subtree_detection_codes(cspm_tree_nodes_list=nodes_of_A)
    # print()
    # print_subtree_detection_codes(cspm_tree_nodes_list=nodes_of_B)
    a_ptr, b_ptr = 0, 0
    assert (len(nodes_of_A) >= len(nodes_of_B))  # as in underlying and super pattern
    while a_ptr < len(nodes_of_A):
        # print(f"pattern_node={nodes_of_B[b_ptr].subtree_detection_code} super_pattern_node={nodes_of_A[a_ptr].subtree_detection_code}")
        subtree_verdict = same_subtree_checking(pattern_node=nodes_of_B[b_ptr], super_pattern_node=nodes_of_A[a_ptr])
        # print(a_ptr, b_ptr, subtree_verdict)
        # print("verdict ",subtree_verdict)
        # can not be > 0: comes from pattern absorption idea, we have (b) and (a,b) must be in the same subtree
        if subtree_verdict == 0 and nodes_of_A[a_ptr].event_no == nodes_of_B[b_ptr].event_no:
            # same subtree and same event number, super pattern should be enough
            a_ptr += 1
        elif subtree_verdict == 0 and nodes_of_A[a_ptr].event_no > nodes_of_B[b_ptr].event_no:
            return False  # A can not completely absorb B, A's occurrence not in the same event
        elif subtree_verdict > 0:
            b_ptr += 1
        else:
            print("WTF ",subtree_verdict, nodes_of_A[a_ptr].subtree_detection_code, nodes_of_A[b_ptr].subtree_detection_code)
            print_subtree_detection_codes(cspm_tree_nodes_list=nodes_of_A)
            print_subtree_detection_codes(cspm_tree_nodes_list=nodes_of_B)
            v=1
            assert(v==0)

    return True  # A can fully absorb B including nodes , ends in same event always


def closure_check(linked_list_nodes, p):
    # P is the pattern, linked_list_nodes: CandidatePatternLinkedListNode/ClosedPatternsLinkedList
    curr = linked_list_nodes # the head
    curr = curr.next
    L1, L2 = [], [] # L1: Existing enclosing p and L2: P enclosing existing
    while curr is not None:
        if isinstance(curr, CandidatePatternLinkedListNode):
            # Optimization for CandidatePatternLinkedListNodes
            if curr.work_with_sex is True and two_pattern_enclose_check(A=p, B=curr.pattern) is True:
                # If curr is already enclosed and absorbed, p can't make any affect on it
                L2.append(curr)
            elif two_pattern_enclose_check(A=curr.pattern, B=p) is True:
                L1.append(curr)
        else:
            if two_pattern_enclose_check(A=p, B=curr.pattern) is True:
                L2.append(curr)
            elif two_pattern_enclose_check(A=curr.pattern, B=p) is True:
                L1.append(curr)
        curr = curr.next
    return L1, L2


def absorption_check(list_of_ll_nodes, nodes_of_p, flag, NODE_MAPPER=None, fast_return=False):
    # flag 0: list_of_ll_nodes have enclosed pattern p
    # flag 1: p has absorbed list_of_ll_nodes
    absorption_status = []
    for i in range(0, len(list_of_ll_nodes)):
        cspm_tree_nodes = []
        if list_of_ll_nodes[i].cspm_tree_nodes is not None:
            cspm_tree_nodes = list_of_ll_nodes[i].cspm_tree_nodes
        elif list_of_ll_nodes[i].cspm_tree_node_bitset is not None:
            cspm_tree_nodes = generate_cspm_tree_nodes_from_bitset(
                cspm_tree_node_bitset=list_of_ll_nodes[i].cspm_tree_node_bitset,NODE_MAPPER=NODE_MAPPER)
        if flag == 0:
            verdict = two_pattern_absorption_check(nodes_of_A=cspm_tree_nodes, nodes_of_B=nodes_of_p)
        elif flag == 1:
            verdict = two_pattern_absorption_check(nodes_of_A=nodes_of_p, nodes_of_B=cspm_tree_nodes)
        absorption_status.append(verdict) # True: absorbs, False: Does not absorb
        if fast_return is True and verdict is True:
            assert(flag == 0) # list_of_all_nodes have enclosed P
            break
    return absorption_status






