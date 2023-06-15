
from debug_functions import DebugFunctions
debug_obj = DebugFunctions()

# index of nodes to track
global_node_count = 0

# Node mapper
HOOK_BITSET_BASED_NODE_PROJECTION = None
NODE_MAPPER = None
# Two powers
TWO_POWERS = {} # 4: 2, 8: 3


def return_node_mapper():
    # return {1: node, 2: node, 3: node, .... }
    global NODE_MAPPER
    return NODE_MAPPER


def set_node_mapper_flag(flag=False):
    # if flag is not None, then NODE_MAPPER is used
    global HOOK_BITSET_BASED_NODE_PROJECTION, NODE_MAPPER
    if flag is True:
        NODE_MAPPER = {}
    HOOK_BITSET_BASED_NODE_PROJECTION = flag
    return


class CSPMTree:
    def __init__(self):
        self.node_id = 0  # each node will have a particular node number
        self.item = None  # item
        self.event_no = -1  # event no
        self.parent_node = None
        self.parent_item_bitset = 0  # bitset value
        self.child_link = None  # [item, event_no] combination
        self.count = 0  # how many times this node has been visited

        # for traversal through next link for ancestor nodes
        self.side_next_link_prev = None
        self.side_next_link_next = None

        # next link section #
        self.down_next_link_ptr = None  # {a:st,end; b:st, en}

        # item freq attribute
        self.item_freq = None

        #subtree detection
        self.subtree_detection_code = ""
        self.depth = 0
        #############

    def initializing_sp_tree_node(self, item, event_no, parent_node, parent_item_bitset, count):
        global global_node_count, NODE_MAPPER, TWO_POWERS
        # global_node_count += 1
        # print("Global node count ", global_node_count)
        node = CSPMTree()
        # node.node_id = global_node_count
        node.item = item
        node.event_no = event_no
        node.parent_node = parent_node
        node.parent_item_bitset = parent_item_bitset
        node.count = count
        # subtree detection code
        node.subtree_detection_code = ""
        # storing the node
        # NODE_MAPPER[1 << global_node_count] = node
        return node

    def insert(self, sp_tree_node, processed_sequence, event_no, item_no, event_bitset):
        # print("event ", event_no, item_no)
        global global_node_count
        if event_no >= len(processed_sequence):
            return
        if item_no >= len(processed_sequence[event_no]):
            self.insert(sp_tree_node, processed_sequence, event_no + 1, 0, 0)
            return
        item = processed_sequence[event_no][item_no]
        if sp_tree_node.child_link is None:
            sp_tree_node.child_link = {}
        if sp_tree_node.child_link.get(item) is None:
            sp_tree_node.child_link[item] = {}
        node = sp_tree_node.child_link[item].get(event_no)  # 0 based, event_no
        if node is None:
            node = self.initializing_sp_tree_node(item=item, event_no=event_no, parent_node=sp_tree_node,
                                                  parent_item_bitset=event_bitset, count=0)
            sp_tree_node.child_link[item][event_no] = node
        node.count += 1
        self.insert(sp_tree_node=node, processed_sequence=processed_sequence, event_no=event_no, item_no=item_no + 1,
                    event_bitset=event_bitset | (1 << item))
        return

    def get_next_link_nodes(self, node, item):
        # get all the next link nodes with support
        save = []
        support = 0
        if node.down_next_link_ptr is not None and node.down_next_link_ptr.get(item) is not None:
            st = node.down_next_link_ptr[item][0]
            en = node.down_next_link_ptr[item][1]
            nxt = st
            while True:
                save.append(nxt)
                support += nxt.count
                if nxt == en:
                    break
                nxt = nxt.side_next_link_next
        return save, support

    def nextlink_gen_using_dfs(self, node):
        global global_node_count, NODE_MAPPER, HOOK_BITSET_BASED_NODE_PROJECTION
        global_node_count += 1
        node.node_id = global_node_count
        if HOOK_BITSET_BASED_NODE_PROJECTION is not None:
            # if this flag is set, then we store the node mapper, we shall use bit based unwrapping technique
            NODE_MAPPER[1<<node.node_id] = node
        # generating next links using bfs
        _dict = {}
        node.down_next_link_ptr = None
        cnt = 0
        if node.child_link is not None:
            for item in node.child_link:
                for event_no in node.child_link[item]:
                    child = node.child_link[item][event_no]
                    cnt += 1
                    child.subtree_detection_code = node.subtree_detection_code + str(cnt)
                    child.depth = node.depth + 1
                    self.nextlink_gen_using_dfs(child)
                    if node.down_next_link_ptr is None:
                        node.down_next_link_ptr = {}
                    if node.down_next_link_ptr.get(child.item) is None:
                        node.down_next_link_ptr[child.item] = [child, child]
                    else:
                        assert(child.node_id > node.down_next_link_ptr[child.item][1].node_id)
                        node.down_next_link_ptr[child.item][1].side_next_link_next = child
                        child.side_next_link_prev = node.down_next_link_ptr[child.item][1]
                        node.down_next_link_ptr[child.item][1] = child
                    if child.down_next_link_ptr is None:
                        continue
                    for key in child.down_next_link_ptr:
                        if key != child.item:
                            if node.down_next_link_ptr.get(key) is None:
                                node.down_next_link_ptr[key] = [child.down_next_link_ptr[key][0],
                                                                child.down_next_link_ptr[key][1]]
                            else:
                                node.down_next_link_ptr[key][1].side_next_link_next = \
                                    child.down_next_link_ptr[key][0]
                                child.down_next_link_ptr[key][0].side_next_link_prev = node.down_next_link_ptr[key][1]
                                node.down_next_link_ptr[key][1] = child.down_next_link_ptr[key][1]
        return