class DebugFunctions:
    def __int__(self):
        pass

    def DebugPrintNextLink(self, node, down_nodes, down_nodes_codes=None):
        # print next links
        down_nodes[node.node_id] = {}
        if down_nodes_codes is not None:
            down_nodes_codes[node.node_id] = {}
        if node.down_next_link_ptr is not None:
            for key in node.down_next_link_ptr:
                down_nodes[node.node_id][key] = []
                if down_nodes_codes is not  None:
                    down_nodes_codes[node.node_id][key] = []
                st = node.down_next_link_ptr[key][0]
                en = node.down_next_link_ptr[key][1]
                #print(st, en)
                nxt = st
                #print("started ")
                while True:
                    down_nodes[node.node_id][key].append(nxt.node_id)
                    down_nodes_codes[node.node_id][key].append(nxt.subtree_detection_code)
                    if (nxt == en):
                        break
                    nxt = nxt.side_next_link_next
        if node.child_link is not None:
            for item in node.child_link:
                for event in node.child_link[item]:
                    self.DebugPrintNextLink(node.child_link[item][event], down_nodes, down_nodes_codes)
        return

    def sanity_test_next_links(self, node):
        down_nodes1 = {}
        down_nodes_codes = {}
        self.bruteforce_nextlink_gen(node, down_nodes1)
        down_nodes2 = {}
        self.DebugPrintNextLink(node, down_nodes2, down_nodes_codes)
        print(down_nodes1)
        print(down_nodes2)
        print(down_nodes_codes)
        for n1 in down_nodes1:
            assert(down_nodes2.get(n1) is not None)
            for it in down_nodes1[n1]:
                assert(down_nodes2[n1].get(it) is not None) # item exists
                down_nodes1[n1][it].sort()
                down_nodes2[n1][it].sort()
                print(n1, it, down_nodes1[n1][it], down_nodes2[n1][it])

    def bruteforce_nextlink_gen(self, node, down_nodes):
        down_nodes[node.node_id] = {}
        _dict = {}
        if node.child_link is not None:
            for item in node.child_link:
                for event_no in node.child_link[item]:
                    child = node.child_link[item][event_no]
                    _dict = self.bruteforce_nextlink_gen(child, down_nodes)
                    for key in _dict:
                        if down_nodes[node.node_id].get(key) is None:
                            down_nodes[node.node_id][key] = []
                        for i in range(0, len(_dict[key])):
                            if _dict[key][i] not in down_nodes[node.node_id][key]:
                                down_nodes[node.node_id][key].append(_dict[key][i])
        if node.item != "":
            _dict[node.item] = [node.node_id]
            for key in down_nodes[node.node_id]:
                if key != node.item:
                    if _dict.get(key) is None:
                        _dict[key] = []
                    for i in range(0, len(down_nodes[node.node_id][key])):
                        _dict[key].append(down_nodes[node.node_id][key][i])
        return _dict

    def moves(self, st, en):
        _list = []
        while True:
            _list.append(st.node_id)
            st = st.side_next_link_next
            if st == en:
                _list.append(en.node_id)
                break
            if st == None:
                break
        return _list

    def print_set_of_nodes(self, nodes):
        for i in range(0, len(nodes)):
            print(f"node={nodes[i].node_id}, support={nodes[i].count} label={nodes[i].item}")

    def print_ll_nodes_pattern(self, list_off_ll_nodes):
        for i in range(0, len(list_off_ll_nodes)):
            print(list_off_ll_nodes[i].pattern)