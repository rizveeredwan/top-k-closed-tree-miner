def check_projection_status(projection_status):
    for i in range(0, len(projection_status)):
        if projection_status[i] == 0:
            return False # This pattern's all the projections are not completete
    return True


def calculate_length(pattern):
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
        return False # projection nodes are not same
    for i in range(0, len(projection_node_a)):
        if projection_node_a[i] == projection_node_b[i]:
            continue
        else:
            return False # projection nodes are not same
    return True # all the projection nodes are the same


def enclosure_absorption_check(pattern, cspm_tree_nodes, projection_status, caph_node, pattern_type):
    enclosure_verdict = check_projection_status(projection_status=projection_status)
    if enclosure_verdict is False:
        return
    # projection is complete
    length = calculate_length(pattern=pattern)
    # will search in 1-less length
    if caph_node.stored_patterns[pattern_type] is not None and \
            caph_node.stored_patterns[pattern_type].get(length-1) is not None:
        head = caph_node.stored_patterns[pattern_type][length-1][0]
        while head is not None:
            small_patt = head.pattern
            big_patt = pattern
            if small_patt is not None and check_projection_status(head.projection_status) is True:
                # not empty pattern and projection is complete - can check now
                enclosure_verdict = two_pattern_enclose_check(A=big_patt, B=small_patt)
                if enclosure_verdict is True: # enclosed
                    head.closed_flag = 0 # can never be closed
                    if big_patt[-1][-1] == small_patt[-1][-1]: # last event matched - might be absorbed
                        absorption_verdict = absorption_check(projection_node_a=head.cspm_tree_nodes,
                                                              projection_node_b=cspm_tree_nodes)
                        if absorption_verdict is True: # enclosed+absorbed
                            head.s_ex_needed = 0 # No SE needed
            head = head.next
    return

