from utilities import *
from math import sqrt

def check_subset(big, small):
    j = 0
    not_found = 0
    for i in range(0, len(small)):
        found = False
        while j < len(big):
            if big[j] == small[i]:
                found = True
                j += 1
                break
            elif big[j] > small[i]:
                break
            else:
                j += 1
        if found is False:
            not_found += 1
    return not_found


def merge_two_events(ev_a, ev_b):
    i , j = 0, 0
    new_ev = []
    while i < len(ev_a) or j < len(ev_b):
        if i < len(ev_a) and j < len(ev_b):
            if ev_a[i] < ev_b[j]:
                new_ev.append(ev_a[i])
                i += 1 
            elif ev_a[i] > ev_b[j]:
                new_ev.append(ev_b[j])
                j += 1
            else:
                new_ev.append(ev_a[i])
                i += 1
                j += 1
        elif i < len(ev_a):
            new_ev.append(ev_a[i])
            i += 1
        elif j < len(ev_b):
            new_ev.append(ev_b[j])
            j += 1
    return new_ev



def min_operation_subset_dp(larger_pattern, smaller_pattern, INF=100000000):
    dp = {}
    # Base Case
    for i in range(0, len(larger_pattern) + 1):
        dp[i] = {}
        for j in range(0, len(smaller_pattern) + 1):
            dp[i][j] = INF
    dp[0][0] = 0
    for i in range(1, len(smaller_pattern) + 1):
        dp[0][i] = dp[0][i-1] + len(smaller_pattern[i-1])
    for i in range(1, len(larger_pattern) + 1):
        dp[i][0] = 0
    # Iteration
    for i in range(1, len(larger_pattern) + 1):
        for j in range(1, len(smaller_pattern) + 1):
            value = check_subset(big=larger_pattern[i-1], small=smaller_pattern[j-1])
            dp[i][j] = min(dp[i - 1][j], value + dp[i-1][j - 1])
    return dp


def min_operation_subset_dp_print(dp, larger_pattern, smaller_pattern):
    merged_pattern = []
    i, j = len(larger_pattern), len(smaller_pattern)
    while True:
        if i == 0:
            while j > 0:
                merged_pattern.append(smaller_pattern[j-1])
                j -= 1
            break
        value = check_subset(big=larger_pattern[i - 1], small=smaller_pattern[j - 1])
        if j>0 and (dp[i][j] == (dp[i-1][j-1]+value)): # itemset
            new_ev = merge_two_events(ev_a=larger_pattern[i - 1], ev_b=smaller_pattern[j - 1])
            merged_pattern.append(new_ev)
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i-1][j]:
            merged_pattern.append(larger_pattern[i-1])
            i -= 1
    merged_pattern.reverse()
    return merged_pattern



def conversion(a):
    _str = []
    for i in range(0, len(a)):
        for j in range(0, len(a[i])):
            _str.append(a[i][j])
        _str.append(-1)
    return _str


def number_of_characters(a):
    _sum = 0
    for i in range(0, len(a)):
        _sum += len(a[i])
    return _sum


def subset_distance(a, b):
    num_a = number_of_characters(a)
    num_b = number_of_characters(b)
    INF = num_a + num_b + 10
    dp1 = min_operation_subset_dp(larger_pattern=a, smaller_pattern=b, INF=INF)
    assert(dp1[len(a)][len(b)] <= num_b)
    # print(dp1[len(a)][len(b)], dp1[len(a)][len(b)]/(num_b*1.0))
    dp2 = min_operation_subset_dp(larger_pattern=b, smaller_pattern=a, INF=INF)
    assert (dp2[len(b)][len(a)] <= num_a)
    # print(dp2[len(b)][len(a)], dp2[len(b)][len(a)]/(num_a*1.0))
    if dp1[len(a)][len(b)]/(num_b*1.0) <= dp2[len(b)][len(a)]/(num_a*1.0):
        return dp1[len(a)][len(b)]/(num_b*1.0), 'a', dp1
    else:
        return dp2[len(b)][len(a)]/(num_a*1.0), 'b', dp2


def characters_between_events(ev1, ev2):
    # checking how many characters are same in between
    j = 0
    match = 0
    for i in range(0, len(ev1)):
        while j < len(ev2):
            if ev1[i] == ev2[j]:
                match += 1
                break
            j += 1
    return match


def lcs_similarity(a, b):
    # Longest Common Subsequence based distance
    dp = {}
    # Base Case
    for i in range(0, len(a) + 1):
        dp[i] = {}
        for j in range(0, len(b) + 1):
            dp[i][j] = 0
    dp[0][0] = 0
    # iteration
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            dp[i][j] = dp[i-1][j-1] + characters_between_events(ev1=a[i-1], ev2=b[j-1])
            dp[i][j] = max(dp[i][j], dp[i-1][j])
            dp[i][j] = max(dp[i][j], dp[i][j-1])
    return dp[len(a)][len(b)]/(1.0 * max(number_of_characters(a), number_of_characters(b)))


def _intersection(set_a, set_b, projection_order_preserved):
    _sum = 0
    if projection_order_preserved is True:
        # can make the searching faster
        i, j = 0, 0
        while i < len(set_a) and j < len(set_b):
            if set_b[j] == set_a[i]:
                _sum += set_a[i].count
                if set_a[i].child_link is not None:
                    # has some child node beneath
                    for ev in set_a[i].child_link:
                        for it in ev:
                            # saving the difference between the parent's count and children's count
                            _sum -= set_a[i].child_link[ev][it].count
                i += 1
                j += 1
            else:
                if set_b[j].node_id < set_a[i].node_id: # need to increase j ptr to get nodes of higher id in set b
                    j += 1
                elif set_b[j].node_id > set_a[i].node_id: # this i ptr can not be matched, need to increase i ptr here
                    i += 1
        return _sum
    else:
        # generic bruteforce searching
        for i in range(0, len(set_a)):
            if set_a[i] in set_b:
                _sum += set_a[i].count
                if set_a[i].child_link is not None:
                    for ev in set_a[i].child_link:
                        for it in ev:
                            # saving the difference between the parent's count and children's count
                            _sum -= set_a[i].child_link[ev][it].count
    return _sum


def _union(set_a, set_b, projection_order_preserved):
    _sum = 0
    if projection_order_preserved is True:
        # can make the searching faster
        i, j = 0, 0
        while i < len(set_a) or j < len(set_b):
            if i < len(set_a) and j < len(set_b):
                if set_b[j] == set_a[i]:
                    _sum += set_a[i].count
                    if set_a[i].child_link is not None:
                        for ev in set_a[i].child_link:
                            for it in ev:
                                # saving the difference between the parent's count and children's count
                                _sum -= set_a[i].child_link[ev][it].count
                    i += 1
                    j += 1
                elif set_a[i].node_id < set_b[j].node_id:
                    _sum += set_a[i].count
                    if set_a[i].child_link is not None:
                        for ev in set_a[i].child_link:
                            for it in ev:
                                # saving the difference between the parent's count and children's count
                                _sum -= set_a[i].child_link[ev][it].count
                    i += 1
                elif set_b[j].node_id < set_a[i].node_id:
                    _sum += set_b[j].count
                    if set_b[j].child_link is not None:
                        for ev in set_b[j].child_link:
                            for it in ev:
                                # saving the difference between the parent's count and children's count
                                _sum -= set_b[j].child_link[ev][it].count
                    j += 1
            elif i < len(set_a):
                _sum += set_a[i].count
                if set_a[i].child_link is not None:
                    for ev in set_a[i].child_link:
                        for it in ev:
                            # saving the difference between the parent's count and children's count
                            _sum -= set_a[i].child_link[ev][it].count
                i += 1
            elif j < len(set_b):
                _sum += set_b[j].count
                if set_b[j].child_link is not None:
                    for ev in set_b[j].child_link:
                        for it in ev:
                            # saving the difference between the parent's count and children's count
                            _sum -= set_b[j].child_link[ev][it].count
                j += 1
    else:
        # generic bruteforce searching
        _sum = 0
        for i in range(0, len(set_a)):
            _sum += set_a[i].count
            for ev in set_a[i].child_link:
                for it in ev:
                    # saving the difference between the parent's count and children's count
                    _sum -= set_a[i].child_link[ev][it].count
        for i in range(0, len(set_b)):
            _sum += set_b[i].count
            for ev in set_b[i].child_link:
                for it in ev:
                    # saving the difference between the parent's count and children's count
                    _sum -= set_b[i].child_link[ev][it].count
        _sum = _sum - _intersection(set_a=set_a, set_b=set_b, projection_order_preserved=projection_order_preserved)
    return _sum


def transaction_wise_distance(a, b, cspm_root, projection_a=None, projection_b=None, projection_order_preserved=False):
    # Transaction wise distance Metric
    # First get the projected nodes
    if projection_a is None:
        projection_a = []
        search_projection_nodes(node=cspm_root, pattern=a, ev=0, it=0, projection_nodes=projection_a)
    if projection_b is None:
        projection_b = []
        search_projection_nodes(node=cspm_root, pattern=b, ev=0, it=0, projection_nodes=projection_b)
    # Second get the leaf nodes/Pseudo Leaf nodes
    leaf_a = []
    for i in range(0, len(projection_a)):
        find_leaf_nodes(current_node=projection_a[i], leaf_nodes=leaf_a)
    leaf_b = []
    for i in range(0, len(projection_b)):
        find_leaf_nodes(current_node=projection_b[i], leaf_nodes=leaf_b)
    # Third calculate the intersection and union
    projection_order_preserved = check_projection_order(projection_nodes=leaf_a) & check_projection_order(projection_nodes=leaf_b)
    assert(projection_order_preserved is True)
    lob = _intersection(set_a=leaf_a, set_b=leaf_b, projection_order_preserved=projection_order_preserved)
    hor = _union(set_a=leaf_a, set_b=leaf_b, projection_order_preserved=projection_order_preserved)
    result = 1.0 - (lob/hor*1.0)
    # Report the metrics output
    return result


def distance(a, b, cspm_root, projection_a=None, projection_b=None, print_flag = False, alpha=0.25, beta=0.25, gamma=0.5):
    # calculating distance between pattern a and pattern b
    td = transaction_wise_distance(a, b, cspm_root, projection_a=projection_a, projection_b=projection_b)
    lcsd = 1.0 - lcs_similarity(a, b)
    sfd, _ , _ = subset_distance(a,b)
    value = alpha * td + beta * lcsd + gamma * sfd
    if print_flag is True:
        print(f"td = {td} lcsd = {lcsd} sfd = {sfd}")
    return value, td, lcsd, sfd


if __name__ == "__main__":
    a = [[1],[4,5], [2]]
    b = [[1, 2], [3]]
    print(subset_distance(a=a, b=b))
    # print(subset_distance(a,b))