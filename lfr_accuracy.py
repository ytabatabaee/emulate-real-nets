from sklearn.metrics.cluster import normalized_mutual_info_score, adjusted_mutual_info_score, adjusted_rand_score
import numpy as np
import argparse

def membership_to_partition(membership):
    part_dict = {}
    for value in membership:
        if value in part_dict:
            part_dict[value] += 1
        else:
            part_dict[value] = 1
    return list(part_dict.values())


def get_membership_list_shared_nodes(gt_path, f1_path, f2_path):
    gt_membership = dict()
    membership1 = dict()
    membership2 = dict()
    with open(gt_path) as fgt:
        for line in fgt:
            i, m = line.strip().split()
            gt_membership[int(i)] = m
    with open(f1_path) as f1:
        for line in f1:
            i, m = line.strip().split()
            membership1[int(i)] = m
    with open(f2_path) as f2:
        for line in f2:
            i, m = line.strip().split()
            membership2[int(i)] = m
    print('#nodes in ground-truth:', len(gt_membership.keys()))
    print('#nodes in pre-CM partition:', len(membership1.keys()))
    print('#nodes in post-CM partition:', len(membership2.keys()))
    keys = list(set(membership2.keys()) & set(membership1.keys()) & set(gt_membership.keys()))
    keys.sort()
    print('common nodes between all partitions:', len(keys))
    mem1 = {i: membership1[i] for i in keys}
    mem2 = {i: membership2[i] for i in keys}
    memgt = {i: gt_membership[i] for i in keys}
    return list(memgt.values()), list(mem1.values()), list(mem2.values())


def get_membership_list_add_singletons(gt_path, f1_path, f2_path):
    gt_membership = dict()
    membership1 = dict()
    membership2 = dict()
    with open(gt_path) as fgt:
        for line in fgt:
            i, m = line.strip().split()
            gt_membership[int(i)] = m
    with open(f1_path) as f1:
        for line in f1:
            i, m = line.strip().split()
            membership1[int(i)] = m
    with open(f2_path) as f2:
        for line in f2:
            i, m = line.strip().split()
            membership2[int(i)] = m
    print('#nodes in ground-truth:', len(gt_membership.keys()))
    print('#nodes in pre-CM partition:', len(membership1.keys()))
    print('#nodes in post-CM partition:', len(membership2.keys()))
    keys = list(gt_membership.keys())
    keys.sort()
    mem_gt = {i: gt_membership[i] for i in keys}
    mem1 = dict()
    mem2 = dict()
    for i in keys:
        if i in membership1:
            mem1[i] = membership1[i]
        else:
            mem1[i] = i
        if i in membership2:
            mem2[i] = membership2[i]
        else:
            mem2[i] = i
    print('#singletons added to post-CM clustering:', len(set(membership2.values())) - len(set(mem2.values())))
    print(len(set(mem_gt.keys())), len(set(mem1.keys())), len(set(mem2.keys())))
    return list(mem_gt.values()), list(mem1.values()), list(mem2.values())



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LFR accuracy for pre-CM vs post-CM partitions")
    parser.add_argument("-gt", "--groundtruth", type=str, required=True,
                        help="File containing ground-truth community membership")
    parser.add_argument("-p1", "--partition1", type=str, required=True,
                        help="File containing original (pre-CM) community membership")
    parser.add_argument("-p2", "--partition2", type=str, required=True,
                        help="File containing post-CM community membership")
    args = parser.parse_args()
    gt_membership, membership1, membership2 = get_membership_list_add_singletons(args.groundtruth, args.partition1, args.partition2)

    cluster_sizes = membership_to_partition(gt_membership)
    cluster_num = len(cluster_sizes)
    print('Ground-truth statistics:')
    print('cluster count:', cluster_num)
    min_size, max_size, mean_size, median_size = int(np.min(cluster_sizes)), int(np.max(cluster_sizes)), \
                                                 np.mean(cluster_sizes), np.median(cluster_sizes)
    print('min, max, mean, median cluster sizes:', min_size, max_size, mean_size, median_size)

    # https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics.cluster
    print('Statistics for original Leiden clustering:')
    print("Normalized mutual information (NMI): ", normalized_mutual_info_score(gt_membership, membership1))
    print("Adjusted rand index (ARI): ", adjusted_rand_score(gt_membership, membership1))
    print("Adjusted mutual information (AMI): ", adjusted_mutual_info_score(gt_membership, membership1))


    print('Statistics for post-CM Leiden clustering:')
    print("Normalized mutual information (NMI): ", normalized_mutual_info_score(gt_membership, membership2))
    print("Adjusted rand index (ARI): ", adjusted_rand_score(gt_membership, membership2))
    print("Adjusted mutual information (AMI): ", adjusted_mutual_info_score(gt_membership, membership2))

