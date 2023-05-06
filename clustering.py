# To summarize a group of patterns
# We can apply K centroid clustering over all the patterns to find K representative patterns
# We can choose maximal pattern based approach to find representative(s) for each group of pattern
import random

from pattern_distance import distance
from maximal_pattern_find import calculate_maximal_pattern_hard_constraint_greedy, \
    calculate_maximal_pattern_light_constraint
from utilities import search_projection_nodes


class ClusterEntity:
    def __init__(self, rpr, cluster_members):
        self.rpr = rpr
        self.cluster_members = cluster_members


def intra_cluster_distance(entity, group_of_patterns, cspm_root, projection_nodes):
    _sum = 0
    cnt = 0
    for i in range(0, len(entity.cluster_members)):
        for j in range(0, len(entity.cluster_members)):
            if i == j:
                continue
            _sum += distance(a=group_of_patterns[entity.cluster_members[i]], b=group_of_patterns[entity.cluster_members[j]],
                             cspm_root=cspm_root, projection_a=projection_nodes[entity.cluster_members[i]],
                             projection_b=projection_nodes[entity.cluster_members[j]])
            cnt += 1
    if cnt == 0:
        cnt = 1
    return (_sum * 1.0)/cnt


def inter_cluster_distance(entities, group_of_patterns, i, j, cspm_root, projection_nodes):
    _sum = 0
    for elm1 in range(0, len(entities[i].cluster_members)):
        for elm2 in range(0, len(entities[j].cluster_members)):
            _sum += distance(a=group_of_patterns[entities[i].cluster_members[elm1]],
                             b=group_of_patterns[entities[j].cluster_members[elm2]],
                             cspm_root=cspm_root, projection_a=projection_nodes[entities[i].cluster_members[elm1]],
                             projection_b=projection_nodes[entities[j].cluster_members[elm2]])
    _sum = _sum / (1.0 * len(entities[i].cluster_members) * len(entities[j].cluster_members))
    return _sum


def print_cluster_stat(entities, group_of_patterns, cspm_root, intra_dist_flag=False, inter_dist_flag=False):
    projection_nodes = []
    for i in range(0, len(group_of_patterns)):
        projection_nodes.append([])
        search_projection_nodes(node=cspm_root, pattern=group_of_patterns[i], ev=0, it=0, projection_nodes=projection_nodes[-1])
    for i in range(0, len(entities)):
        print(f"{i+1}:rpr {group_of_patterns[entities[i].rpr]}")
        for j in range(0,len(entities[i].cluster_members)):
            print(f"{group_of_patterns[entities[i].cluster_members[j]]}")
        if intra_dist_flag is True:
            intra_dis = intra_cluster_distance(entity=entities[i], group_of_patterns=group_of_patterns,
                                               cspm_root=cspm_root, projection_nodes=projection_nodes)
            print(f"intra={round(intra_dis, 2)}")
    if inter_dist_flag is True:
        for i in range(0, len(entities)):
            print(f"for {i}: ")
            for j in range(i, len(entities)):
                dist = inter_cluster_distance(entities, group_of_patterns, i, j, cspm_root, projection_nodes)
                print(f"inter={round(dist, 2)}")
        return


def divide_into_clusters(k, group_of_patterns, entities, cspm_root, projection_nodes):
    # based on the representatives, we are dividing the patterns into the group of different clusters
    for i in range(0, len(entities)):
        entities[i].cluster_members.clear()
    for i in range(0, len(group_of_patterns)):
        best_rpr = None
        min_dist = None
        patt = group_of_patterns[i]
        for j in range(0, len(entities)):
            rpr_pattern = group_of_patterns[entities[j].rpr]
            dist = distance(a=patt, b=rpr_pattern, cspm_root=cspm_root, projection_a=projection_nodes[i],
                            projection_b=projection_nodes[entities[j].rpr])
            if min_dist is None or min_dist > dist:
                min_dist = dist
                best_rpr = j
        entities[best_rpr].cluster_members.append(i)  # ith pattern in that cluster
    return entities


def find_reprsentative(group_of_patterns, single_entitity, cspm_root, projection_nodes):
    # for this single cluster, picking up the point/represntative that gives the least average distance
    min_dist = None
    best_rpr = None
    for i in range(0, len(single_entitity.cluster_members)):
        rpr_patt = group_of_patterns[single_entitity.cluster_members[i]]
        dist_sum = 0
        for j in range(0, len(single_entitity.cluster_members)):
            patt = group_of_patterns[single_entitity.cluster_members[j]]
            dist = distance(a=rpr_patt, b=patt, cspm_root=cspm_root, projection_a=projection_nodes[single_entitity.cluster_members[i]],
                            projection_b=projection_nodes[single_entitity.cluster_members[j]])
            dist_sum += dist
        if len(single_entitity.cluster_members) == 0:
            dist_sum = 0
        else:
            dist_sum /= len(single_entitity.cluster_members) * 1.0
        if min_dist is None:
            min_dist = dist_sum
            best_rpr = single_entitity.cluster_members[i]
        if min_dist > dist_sum:
            min_dist = dist_sum
            best_rpr = single_entitity.cluster_members[i]
    return best_rpr


def k_centroid_clustering(group_of_patterns=[], K=3, max_number_of_iterations=1000, cspm_root=None, tolerance=5):
    # group_of_patterns need to be a list
    # pick random k representative patterns
    entities = []
    projection_nodes = []
    for i in range(0, len(group_of_patterns)):
        projection_nodes.append([])
        search_projection_nodes(node=cspm_root, pattern=group_of_patterns[i], ev=0, it=0,
                                projection_nodes=projection_nodes[-1])
    while len(entities) < K:
        idx = random.randint(0, len(group_of_patterns)-1)
        flag = True
        for i in range(0, len(entities)):
            if entities[i].rpr == idx:
                flag = False
                break
        if flag is True:
            new_entity = ClusterEntity(rpr=idx, cluster_members=[])
            entities.append(new_entity)
    # print(f"starting new repr {[entities[j].rpr for j in range(len(entities))]}")
    entities = divide_into_clusters(k=K, group_of_patterns=group_of_patterns, entities=entities,
                                    cspm_root=cspm_root, projection_nodes=projection_nodes)
    entities.sort(key=lambda x: x.rpr)
    tolerance_cnt = 0
    i = 1
    temp = []
    print(f"starting new repr {[entities[j].rpr for j in range(len(entities))]}")
    while i <= max_number_of_iterations:
        i += 1
        rpr_change = 0
        temp.clear()  # clearing old
        for j in range(0, len(entities)):
            # calculating new representatives
            temp.append(entities[j].rpr)
            new_rpr_idx = find_reprsentative(group_of_patterns=group_of_patterns, single_entitity=entities[j],
                                             cspm_root=cspm_root, projection_nodes=projection_nodes)
            entities[j].rpr = new_rpr_idx
        entities.sort(key=lambda x: x.rpr)
        for j in range(0, len(entities)):
            if entities[j].rpr != temp[j]:
                # representative of this group has change
                rpr_change += 1
        print(f"{i}: new repr {[entities[j].rpr for j in range(len(entities))]}")
        if rpr_change > 0:
            # new representative list has been found, again divide the points based on the distance between the point
            # and the representative
            entities = divide_into_clusters(k=K, group_of_patterns=group_of_patterns, entities=entities,
                                            cspm_root=cspm_root, projection_nodes=projection_nodes)
            tolerance_cnt = 0
        elif rpr_change == 0:
            # No change has been observed
            print(f"No representative change has been observed in {i}th iteration")
            tolerance_cnt += 1
            if tolerance_cnt == tolerance:
                # consecutive many iterations did not see the changes, breaking
                break
            else:
                entities = divide_into_clusters(k=K, group_of_patterns=group_of_patterns, entities=entities,
                                                cspm_root=cspm_root, projection_nodes=projection_nodes)

    print(f"Number of iterations {i} from {max_number_of_iterations} {[entities[j].rpr for j in range(0, len(entities))]}")
    return entities


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
            representatives[support] = [maximal]  # A single maximal pattern for each group of CSPs
    return representatives


if __name__ == "__main__":
    a = [[1], [2]]
    c = [[[1], [2], [3]], [[2], [1]]]
    a = [[] for i in range(3)]
    print(a)
