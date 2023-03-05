# Emulating real networks with LFR graphs
We provide scripts for estimating the parameters of a network and a clustering of that network, and generating a synthetic LFR graph ([Lancichinetti et al., 2008](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.78.046110)) that resembles the characteristics of this network/clustering pair.

## Dependencies
These scripts are implemented in Python 3 and have the following dependencies:
- [LFR benchmark graph software](https://www.santofortunato.net/resources)
- [Python 3.x](https://www.python.org)
- [NetworkX](https://networkx.org)
- [Numpy](https://numpy.org)
- [powerlaw](https://pypi.org/project/powerlaw/)

If you have Python 3 and pip, you can use `pip install -r requirements.txt` to install the other dependencies. We provide the LFR benchmark graph software in `binary_networks` directory, but it can also be downloaded from [https://www.santofortunato.net/resources](https://www.santofortunato.net/resources).

## Usage Instructions

### Estimating parameters of a network/clustering pair
**Input:** A file containing a network edge-list and a file containing clustering memberships on the same network.

**Output:** A file in JSON format named `<clustering_memberships.json>` that provides the following information:

```
$ python3 estimate_properties.py -n <network_edgelist.tsv> -c <clustering_memberships.tsv>
```
**Example output**
```
{
    "node-count": 75025194,
    "edge-count": 1363303678,
    "isolate-count": 0,
    "num-connected-components": 180021,
    "max-connected-components": 74601990,
    "min-degree": 1,
    "max-degree": 223183,
    "mean-degree": 36.34255655506869,
    "median-degree": 19.0,
    "num-clusters": 7849683,
    "min-cluster-size": 1,
    "max-cluster-size": 3678,
    "mean-cluster-size": 9.557735516198552,
    "median-cluster-size": 1.0,
    "num-singletons": 5714531,
    "num-non-singletons": 2135152,
    "modularity-score": 0.3245359347856109,
    "node-coverage": 0.9238318397417273,
    "mixing-parameter": 0.6016065209427944,
    "tau1": 2.973781770763132,
    "xmin1": 517.0,
    "tau2": 2.0791213462000417,
    "xmin2": 20.0,
    "tau1-fixed": 1.296949562166257,
    "xmin1-fixed": 1.0,
    "tau2-fixed": 1.7304042117841385,
    "xmin2-fixed": 1.0
}
```

### Emulating a network/clustering with LFR graphs
**Input:** A JSON file as generated in the previous step, path to the LFR software executable and a minimum community size (for most networks, we do not suggest using values less than 10 for `cmin`, as LFR software would not able to generate the graph in a reasonable time).

**Output:** A directory with the LFR network (`network.dat`) and its ground-turth communities (`community.dat`), as well as statistics of the LFR network/communities (`statistics.dat`).

```
$ python3 gen_lfr.py -n <clustering_memberships.json> -lp <lfr-benchmark-software-path> -cm <cmin_value>
```

The outputs would be located in a directory called `<clustering_memberships>_lfr` and the following will be printed to the screen:
```
../binary_networks//benchmark -N 34546 -k 24.36617842876165 -maxk 846 -mu 0.37999943730019126 -maxc 800 -minc 30 -t1 3.6312283315636975 -t2 1.8497807268067572
setting... -N 34546
setting... -k 24.36617842876165
setting... -maxk 846
setting... -mu 0.37999943730019126
setting... -maxc 800
setting... -minc 30
setting... -t1 3.6312283315636975
setting... -t2 1.8497807268067572

**************************************************************
number of nodes:	34546
average degree:	24.3662
maximum degree:	846
exponent for the degree distribution:	3.63123
exponent for the community size distribution:	1.84978
mixing parameter:	0.379999
number of overlapping nodes:	0
number of memberships of the overlapping nodes:	0
community size range set equal to [30 , 800]
**************************************************************

building communities...
connecting communities...
recording network...


---------------------------------------------------------------------------
network of 34546 vertices and 431138 edges;	 average degree = 24.9602

average mixing parameter: 0.379872 +/- 0.0193649
p_in: 0.240933	p_out: 0.000265551
```
