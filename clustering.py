# To summarize a group of patterns
# We can apply K centroid clustering over all the patterns to find K representative patterns
# We can choose maximal pattern based approach to find representative(s) for each group of pattern
import random

from pattern_distance import distance
from maximal_pattern_find import calculate_maximal_pattern_hard_constraint_greedy, \
    calculate_maximal_pattern_light_constraint

def divide_into_clusters(k, group_of_patterns, representatives, cspm_root):
    # based on the representatives, we are dividing the patterns into the group of different clusters
    fin_clusters = [[] for i in range(k)]
    for i in range(0, len(group_of_patterns)):
        best_rpr = None
        min_dist = None
        patt = group_of_patterns[i]
        for j in range(0, len(representatives)):
            rpr_pattern = group_of_patterns[representatives[j]]
            dist = distance(a=patt, b=rpr_pattern, cspm_root=cspm_root)
            if min_dist is None or min_dist > dist:
                min_dist = dist
                best_rpr = j
        fin_clusters[best_rpr].append(i) # ith pattern in that cluster
    return fin_clusters


def find_reprsentative(group_of_patterns, single_cluster, cspm_root):
    # for this single cluster, picking up the point/represntative that gives the least average distance
    min_dist = None
    best_rpr = None
    for i in range(0, len(single_cluster)):
        rpr_patt = group_of_patterns[single_cluster[i]]
        dist_sum = 0
        for j in range(0, len(single_cluster)):
            patt = group_of_patterns[single_cluster[j]]
            dist = distance(a=rpr_patt, b=patt, cspm_root=cspm_root)
            dist_sum += dist
        if len(single_cluster) == 0:
            dist_sum = 0
        else:
            dist_sum /= len(single_cluster)*1.0
        if min_dist is None:
            min_dist = dist_sum
            best_rpr = i
        if min_dist > dist_sum:
            min_dist = dist_sum
            best_rpr = i
    return best_rpr


def k_centroid_clustering(group_of_patterns=[], k=3, max_number_of_iterations=1000, cspm_root=None, tolerance=5):
    # group_of_patterns need to be a list
    # pick random k representative patterns
    representatives = []
    while len(representatives) < k:
        idx = random.randint(0, len(group_of_patterns))
        if idx not in representatives:
            representatives.append(idx)
    fin_clusters = divide_into_clusters(k=k, group_of_patterns=group_of_patterns, representatives=representatives, cspm_root=cspm_root)
    tolerance_cnt = 0
    i = 1
    while i <= len(max_number_of_iterations):
        i += 1
        rpr_change = 0
        for j in range(0, len(fin_clusters)):
            new_rpr_idx = find_reprsentative(group_of_patterns=group_of_patterns, single_cluster=fin_clusters[j], cspm_root=cspm_root)
            if new_rpr_idx != representatives[j]:
                # representative of this group has change
                rpr_change += 1
                representatives[j] = new_rpr_idx
        if rpr_change > 0:
            # new representative list has been found, again divide the points based on the distance between the point
            # and the representative
            fin_clusters = divide_into_clusters(k=k, group_of_patterns=group_of_patterns, representatives=representatives, cspm_root=cspm_root)
            tolerance_cnt = 0
        elif rpr_change == 0:
            # No change has been observed
            print(f"No representative change has been observed in {i}th iteration")
            tolerance_cnt += 1
            if tolerance_cnt == tolerance:
                # consecutive many iterations did not see the changes, breaking
                break
            else:
                fin_clusters = divide_into_clusters(k=k, group_of_patterns=group_of_patterns,
                                                    representatives=representatives, cspm_root=cspm_root)

    print(f"Number of iterations {i} from {max_number_of_iterations}")
    for i in range(0, len(representatives)):
        representatives[j] = group_of_patterns[representatives[j]]
    return representatives


def summarize_each_group_of_pattern(group_of_patterns, cspm_tree, real_pattern=False):
    # there are two types
    # group_of_patterns need to be dictionary
    # - (real_pattern=False) maximal pattern(s) where the summarized patterns do not need to be an actual pattern found in DB
    # - (real_pattern=True) maximal patterns(s) where the summarized patterns have to be a found pattern in the database
    representatives = {}
    if real_pattern is True:
        representatives = calculate_maximal_pattern_hard_constraint_greedy(group_of_patterns, cspm_tree)
    elif real_pattern is False:
        for support in group_of_patterns:
            maximal = calculate_maximal_pattern_light_constraint(pattern_cluster=group_of_patterns[support])
            representatives[support] = [maximal] # A single maximal pattern for each group of CSPs
    return representatives



if __name__ == "__main__":
    a = [[1], [2]]
    c = [ [[1], [2], [3]] , [[2], [1]] ]
    a = [[] for i in range(3)]
    print(a)