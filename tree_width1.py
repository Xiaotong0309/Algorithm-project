import networkx as nx
from networkx.algorithms import approximation
import matplotlib.pyplot as plt

#find a decomposition with treewidth k
def tree_decomposition(G, k):
    max_nodes = 20
    exist = False
    dcp = []
    #very small graph
    n = nx.number_of_nodes(G)
    if n < max_nodes:
        dcp = treewidth_min_degree(G)
        print(dcp)
        return k, True, dcp
    ne = G.number_of_edges()
    #check
    if ne > k*n-0.5*k*(k+1):
        return k, False, []
    #find a maximal matching
    M = maximal_matching(G)
    print(M)
    #contracting
    G1 = G
    for e in M:
        list1 = list(G.adj[e[0]])
        list2 = list(G.adj[e[1]])
        for v in list1:
            G1.add_edge(e[1], v)
        G1.remove_node(e[0])
    #recursive
    result = tree_decomposition(G1, k)
    if result[1] == False:
        return k, False, []
    else:
        #construct dcp for G
        dcp_pre = result[2]
        #compute fM(v)
        fM = []
        for v in G:
            fM[v] = v
        for e in M:
            if v == e[0]:
                fM[v] = e[1]
        for bag in dcp_pre:
            list = []
            for v in G:
                if fM[v] in bag:
                    list.append(v)
            dcp.append(list)
    return k, exist, dcp


i = 0.1
while i <= 0.1:
    G = nx.planted_partition_graph(2, 20, i, i, seed=42)
    dcp = approximation.treewidth_min_degree(G)
    print(dcp[0])

    plt.subplot(121)
    nx.draw(dcp[1], with_labels=False, font_weight='bold')
    plt.show()
    i += 0.1


#convert to nice tree decomposition
G = nx.planted_partition_graph(2, 10, 0.4, 0.4, seed=42)
dcp = approximation.treewidth_min_degree(G)

n = G.number_of_nodes()

plt.subplot(121)
nx.draw(dcp[1], with_labels=False, font_weight='bold')
plt.show()

#preliminary
dict_v = {}
i = 0
for v in dcp[1]:
    dict_v[i] = v
    dcp[1].nodes[v]['label'] = i
    dcp[1].nodes[v]['state'] = False
    i += 1
counter = i

#convert to tree
def convert_to_tree(G1, index, G2):
    list_v = list(G1.adj[dict_v[index]])
    index_list = []
    for v in list_v:
        if G1.nodes[v]['state'] == False:
            index_nbr = G1.nodes[v]['label']
            G2.add_edge(index, index_nbr)
            G1.nodes[v]['state'] = True
            index_list.append(index_nbr)
    for i in index_list:
        convert_to_tree(G1, i, G2)


tree = nx.DiGraph()
tree.add_node(0)
dcp[1].nodes[dict_v[0]]['state'] = True
convert_to_tree(dcp[1], 0, tree)

plt.subplot(121)
nx.draw(tree, with_labels=False, font_weight='bold')
plt.show()

#convert to binary tree
def check(G):
    for v in G:
        succ = G.successors(v)
        l_succ = list(succ)
        if len(l_succ) > 2:
            return False
    return True
def update(G, index, counter, dict_v):
    succ = G.successors(index)
    l_succ = list(succ)
    if len(l_succ) > 2:
        dict_v[counter] = dict_v[index]
        G.add_node(counter)
        for i in range(1, len(l_succ)):
            G.add_edge(counter, l_succ[i])
            G.remove_edge(index, l_succ[i])
        G.add_edge(index, counter)
        counter += 1
    return counter
i = 0
while check(tree) == False:
    while i < counter:
        counter = update(tree, i, counter, dict_v)
        i += 1

plt.subplot(121)
nx.draw(tree, with_labels=False, font_weight='bold')
plt.show()

#satisfy P4&P5
def froze_to_set(v):
    froze = iter(v)
    f_list = list(froze)
    set_new = set(f_list)
    return set_new
def set_to_froze(v):
    set_list = []
    for e in v:
        set_list.append(e)
    froze_set = frozenset(set_list)
    return froze_set
def check_nice(G, dict_v):
    for v in G:
        succ = G.successors(v)
        l_succ = list(succ)
        if len(l_succ) == 2:
            if dict_v[l_succ[0]] != dict_v[v] or dict_v[l_succ[1]] != dict_v[v]:
                return False
                #add_p4(G, v, l_succ[0])
        elif len(l_succ) == 1:
            set_parent = froze_to_set(dict_v[v])
            set_child = froze_to_set(dict_v[l_succ[0]])
            if (set_parent.issuperset(set_child) == False or len(set_parent.difference(set_child)) != 1)\
            and (set_child.issuperset(set_parent) == False or len(set_child.difference(set_parent)) != 1):
                return False
    return True
def update_nice(G, index, counter, dict_v):
    succ = G.successors(index)
    l_succ = list(succ)
    if len(l_succ) == 2:
        if dict_v[l_succ[0]] != dict_v[index]:
            dict_v[counter] = dict_v[index]
            G.add_node(counter)
            G.add_edge(index, counter)
            G.add_edge(counter, l_succ[0])
            G.remove_edge(index, l_succ[0])
            counter += 1
        if dict_v[l_succ[1]] != dict_v[index]:
            dict_v[counter] = dict_v[index]
            G.add_node(counter)
            G.add_edge(index, counter)
            G.add_edge(counter, l_succ[1])
            G.remove_edge(index, l_succ[1])
            counter += 1
    elif len(l_succ) == 1:
        set_parent = froze_to_set(dict_v[index])
        set_child = froze_to_set(dict_v[l_succ[0]])
        if (set_parent.issuperset(set_child) == False or len(set_parent.difference(set_child)) != 1)\
        and (set_child.issuperset(set_parent) == False or len(set_child.difference(set_parent)) != 1):
            inter_set = set_parent.intersection(set_child)
            disjoint_set_parent = set_parent.difference(inter_set)
            disjoint_set_child = set_child.difference(inter_set)
            new_set = set_parent
            pre_counter = index
            while len(disjoint_set_parent) != 0:
                e = disjoint_set_parent.pop()
                new_set.remove(e)
                new_data = set_to_froze(new_set)
                dict_v[counter] = new_data
                G.add_node(counter)
                G.add_edge(pre_counter, counter)
                G.add_edge(counter, l_succ[0])
                G.remove_edge(pre_counter, l_succ[0])
                if pre_counter == index:
                    pre_counter = counter
                else: pre_counter += 1
                counter += 1
            while len(disjoint_set_child) != 1:
                e = disjoint_set_child.pop()
                new_set.add(e)
                new_data = set_to_froze(new_set)
                dict_v[counter] = new_data
                G.add_node(counter)
                G.add_edge(pre_counter, counter)
                G.add_edge(counter, l_succ[0])
                G.remove_edge(pre_counter, l_succ[0])
                if pre_counter == index:
                    pre_counter = counter
                else: pre_counter += 1
                counter += 1


    return counter
i = 0
while check_nice(tree, dict_v) == False:
    while i < counter:
        counter = update_nice(tree, i, counter, dict_v)
        i += 1
plt.subplot(121)
nx.draw(tree, with_labels=False, font_weight='bold')
plt.show()
