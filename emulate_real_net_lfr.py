import argparse
import random
import time
import community as cm
import igraph as ig
import leidenalg
import networkx as nx
import numpy as np
from collections import Counter
from networkx.generators.community import LFR_benchmark_graph
import matplotlib.pyplot as plt

def plot_dist(dist, name):
    plt.cla()
    plt.grid(linestyle='--', linewidth=0.5)
    #dist = np.log(year_dist['citations'])
    #sns.scatterplot(data=dist, y="citations", x="year", linewidth=0, color='black')  # , kde=True, bins=50)
    x = np.arange(1, len(dist)+1)
    plt.plot(np.log(x), np.log(dist), color='black')
    plt.ylabel('ln (dist)')
    #plt.title('Citations per year in the open-citations dataset')
    #plt.savefig('lfr-.pdf')
    plt.savefig(name+'_dist.pdf')

def communities_to_dict(communities):
    result = {}
    community_index = 0
    for c in communities:
        community_mapping = ({node: community_index for index, node in enumerate(c)})
        result = {**result, **community_mapping}
        community_index += 1
    return result

def get_membership_list_from_dict(membership_dict):
    return [membership_dict[i] for i in range(len(membership_dict))]

def get_membership_list_from_file(file_name):
    membership = []
    with open(file_name) as f:
        for line in f:
            _, m = line.strip().split()
            membership.append(int(m))
    return membership

def relabel_from_zero(net_path, community_path):
    with open(net_path+'_relabeled', 'w') as g:
        with open(net_path) as f:
            for line in f:
                i, j = line.strip().split()
                g.write(str(int(i)-1) + '    ' + str(int(j)-1) + '\n')

    with open(community_path+'_relabeled', 'w') as g:
        with open(community_path) as f:
            for line in f:
                i, m = line.strip().split()
                g.write(str(int(i)-1) + '    ' + str(int(m)-1) + '\n')


def write_membership_list_to_file(file_name, membership):
    with open(file_name, 'w') as f:
        f.write('\n'.join(str(i)+' '+str(membership[i]+1) for i in range(len(membership))))
        #for i in range(len(membership)):
        #    f.write(str(i+1)+' '+str(membership[i]+1)+'\n')

def compute_mixing_param(net, membership):
    n = net.number_of_nodes()
    in_degree = np.zeros(n)
    out_degree = np.zeros(n)

    # iterate over all edges of a graph
    for n1, n2 in net.edges:
        if membership[n1] == membership[n2]: # nodes are co-clustered
            in_degree[n1] += 1
            in_degree[n2] += 1
        else:
            out_degree[n1] += 1
            out_degree[n2] += 1


    mus = [out_degree[i]/(out_degree[i]+in_degree[i]) for i in range(len(in_degree))]
    #print(mus[:20])
    #print(list(in_degree[:20]))
    #print(list(out_degree[:20]))
    print('micro-average', np.mean(mus))
    print('macro-average', np.sum(out_degree)/(np.sum(in_degree)+np.sum(out_degree)))
    mixing_param = np.mean(mus)
    return mixing_param

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Emulating real networks using LFR graphs.')
    parser.add_argument('-n', metavar='net', type=str, required=True,
                        help='network edge-list path')
    parser.add_argument('-c', metavar='clustering', type=str, required=True,
                        help='clustering membership path')
    parser.add_argument('-r', metavar='relabel', required=False, default=False,
                        help='relabel from zero', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    if args.r:
        relabel_from_zero(args.n, args.c)
        args.n = args.n + '_relabeled'
        args.c = args.c + '_relabeled'

    print('- properties of the input network')
    net = nx.read_edgelist(args.n, nodetype=int)
    degrees = sorted([d for _, d in net.degree()])
    min_degree, max_degree, avg_degree, median_degree = np.min(degrees), np.max(degrees), int(
        np.mean(degrees)), np.median(degrees)
    print('#nodes, #edges, avg degree, max degree, min degree', net.number_of_nodes(), net.number_of_edges(),
          avg_degree, max_degree, min_degree)
    #plot_dist(degrees, 'degree')


    membership = get_membership_list_from_file(args.c)
    sizes = Counter(membership).most_common()
    community_size_dist = sorted([c for _, c in sizes])
    #print(community_size_dist)
    #plot_dist(community_size_dist, 'cm_size')
    max_community_size = sizes[0][1]
    min_community_size = sizes[-1][1]
    print('#communities, max comm size, min comm size', len(sizes), max_community_size, min_community_size)

    mixing_param=compute_mixing_param(net, membership)

    print('mu real:', mixing_param)
    #mixing_param = 0.1

    start = time.time()
    lfr = LFR_benchmark_graph(n=net.number_of_nodes(),
                              tau1=3, tau2=1.5,
                              mu=0.4,
                              average_degree=avg_degree, max_degree=max_degree,
                              min_community=20, #max_community=max_community_size,
                              seed=0)
    '''lfr = LFR_benchmark_graph(n=net.number_of_nodes(),
                              tau1=3, tau2=1.5,
                              mu=mixing_param,
                              average_degree=avg_degree, max_degree=100,
                              min_community=20,
                              seed=0)'''
    print('\ntime spent generating the LFR graph (sec):', time.time() - start)


    print('\n- properties of the LFR network')
    nx.write_edgelist(lfr, 'lfr_net_'+str(mixing_param)+'_'+args.n, data=False)
    degrees = [d for n, d in lfr.degree()]
    print('#nodes, #edges, avg degree, max degree, min degree', lfr.number_of_nodes(), lfr.number_of_edges(),
          np.mean(degrees), np.max(degrees), np.min(degrees))

    ground_truth = {frozenset(lfr.nodes[v]["community"]) for v in lfr}
    ground_truth = get_membership_list_from_dict(communities_to_dict([list(c) for c in ground_truth]))
    sizes = Counter(ground_truth).most_common()
    max_community_size = sizes[0][1]
    min_community_size = sizes[-1][1]
    print('#communities, max comm size, min comm size', len(sizes), max_community_size, min_community_size)
    mixing_param=compute_mixing_param(lfr, ground_truth)
    print('mu lfr:', mixing_param)
    write_membership_list_to_file('lfr_comm_'+str(mixing_param)+'_'+args.n, ground_truth)
