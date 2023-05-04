def check_projection_status(projection_status):
    # checking if the pattern is completely projected/having 1 in each projected node
    for i in range(0, len(projection_status)):
        if projection_status[i] == 0:
            return False  # This pattern's all the projections are not completete
    return True


def calculate_length(pattern):
    # calculating the number of characters in the pattern
    _sum = 0
    for i in range(0, len(pattern)):
        _sum += len(pattern[i])
    return _sum


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


def absorption_check(projection_node_a, projection_node_b):
    if len(projection_node_a) != len(projection_node_b):
        return False  # projection nodes are not same
    for i in range(0, len(projection_node_a)):
        if projection_node_a[i] == projection_node_b[i]:
            continue
        else:
            return False  # projection nodes are not same
    return True  # all the projection nodes are the same


def enclosure_absorption_check(pattern, cspm_tree_nodes, projection_status, caph_node, pattern_type):
    enclosed = []
    absorbed = []
    enclosure_verdict = check_projection_status(projection_status=projection_status)
    if enclosure_verdict is False:
        return enclosed, absorbed
    # projection is complete
    length = calculate_length(pattern=pattern)
    if caph_node.stored_patterns[pattern_type] is None:
        return enclosed, absorbed
    lengths = caph_node.stored_patterns[pattern_type].keys()
    cnt = 0
    for small_len in lengths:
        cnt += 1
        if small_len < length:
            # will search in 1-less length
            if caph_node.stored_patterns[pattern_type] is not None and \
                    caph_node.stored_patterns[pattern_type].get(small_len) is not None:
                head = caph_node.stored_patterns[pattern_type][small_len][0]
                while head is not None:
                    small_patt = head.pattern
                    big_patt = pattern
                    # candidate
                    if pattern_type == "candidate" and small_patt is not None and check_projection_status(
                            head.projection_status) is True and head.closed_flag == 1:
                        # pattern is not None, completely projected and still closed
                        # not empty pattern and projection is complete - can check now
                        enclosure_verdict = two_pattern_enclose_check(A=big_patt, B=small_patt)
                        if enclosure_verdict is True:  # enclosed
                            enclosed.append(head)
                            head.closed_flag = 0  # can never be closed
                            if big_patt[-1][-1] == small_patt[-1][-1]:  # last event matched - might be absorbed
                                absorption_verdict = absorption_check(projection_node_a=head.cspm_tree_nodes,
                                                                      projection_node_b=cspm_tree_nodes)
                                if absorption_verdict is True:  # enclosed+absorbed
                                    head.s_ex_needed = 0  # No SE needed
                                    absorbed.append(head) # absorbed
                    # closed
                    if pattern_type == "closed" and small_patt is not None:
                        # not empty pattern and projection is complete - can check now
                        enclosure_verdict = two_pattern_enclose_check(A=big_patt, B=small_patt)
                        if enclosure_verdict is True:  # enclosed
                            enclosed.append(head)
                            head.closed_flag = 0  # can never be closed
                    head = head.next
    return enclosed, absorbed


def find_leaf_nodes(current_node, leaf_nodes):
    # From the current node reach the leaf nodes
    _sum = 0
    for ev in current_node.child_link:
        for it in current_node.child_link[ev]:
            _sum += current_node.child_link[ev][it].count
            find_leaf_nodes(current_node=current_node.child_link[ev][it], leaf_nodes=leaf_nodes)
    if _sum < current_node.count:
        leaf_nodes.append(current_node)  # Pseudo leaf node/leaf node
    return


def extract_the_full_transaction(cspm_tree_node):
    # trying to extract the complete transaction here from leaf to root node
    tr = []
    current = cspm_tree_node
    last_event = None
    while current is not None:
        if last_event != current.event_no:
            if current.item is not None:
                tr.append([current.item])
        else:
            assert (current.item is not None)
            tr[-1].append(current.item)
        last_event = current.event_no
        current = current.parent_node
    tr.reverse()
    for i in range(0, len(tr)):
        tr[i].reverse()
    return tr


def find_bitset(pattern, event, it):
    # For an event construt its bitset
    need = 0
    for i in range(0, it):
        need = need | (1 << pattern[event][i])
    return need


def search_projection_nodes(node, pattern, ev, it, projection_nodes):
    # For the pattern finding its projection nodes in the tree
    if ev == len(pattern):
        projection_nodes.append(node)
        return
    elif it == len(pattern[ev]):
        search_projection_nodes(node=node, pattern=pattern, ev=ev + 1, it=0, projection_nodes=projection_nodes)
    else:
        choices = []
        if node.down_next_link_ptr is not None and node.down_next_link_ptr.get(pattern[ev][it]) is not None:
            start = node.down_next_link_ptr[pattern[ev][it]][0]
            end = node.down_next_link_ptr[pattern[ev][it]][1]
            while True:
                choices.append(start)
                if start == end:
                    break
                start = start.side_next_link_next
        for i in range(0, len(choices)):
            if it == 0:  # SE
                if choices[i].event_no == node.event_no:  # not valid SE
                    search_projection_nodes(choices[i], pattern, ev, it, projection_nodes)
                elif choices[i].event_no > node.event_no:  # valid SE
                    search_projection_nodes(choices[i], pattern, ev, it + 1, projection_nodes)
            else:  # IE
                bitset = find_bitset(pattern=pattern, event=ev, it=it)
                assert (bitset > 0)
                if (choices[i].parent_item_bitset & bitset) == bitset:  # valid IE
                    search_projection_nodes(choices[i], pattern, ev, it + 1, projection_nodes)
                else:  # not valid IE
                    search_projection_nodes(choices[i], pattern, ev, it, projection_nodes)


def check_projection_order(projection_nodes):
    # trying to see if all the nodes are projected in the ascending order of their node ids or not
    for i in range(1, len(projection_nodes)):
        if projection_nodes[i].node_id > projection_nodes[i - 1].node_id:
            continue
        else:
            return False  # did not preserve the order
    return True  # maintained the order
