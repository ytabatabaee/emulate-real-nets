import argparse
import os
import subprocess
import sys


def stats_path_from_clustering(clustering_path):
    return clustering_path.replace('.tsv', '') + ".json"


def run_estimator(estimator_script, network_path, clustering_path):
    cmd = [sys.executable, estimator_script, "-n", network_path, "-c", clustering_path]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def run_lfr(stats_path, lfr_path, cmin):
    cmd = [sys.executable, "gen_lfr.py", "-n", stats_path, "-lp", lfr_path]
    if cmin is not None:
        cmd += ["-cm", str(cmin)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run full pipeline: estimate properties then generate LFR network."
    )
    parser.add_argument("-n", metavar="net", type=str, required=True,
                        help="network edge-list path")
    parser.add_argument("-c", metavar="clustering", type=str, required=True,
                        help="clustering membership path")
    parser.add_argument("-lp", metavar="lfrpath", type=str, required=True,
                        help="LFR software executable path (benchmark)")
    parser.add_argument("-cm", metavar="cmin", type=str, required=False,
                        help="Minimum community size")
    parser.add_argument("--networkit", action="store_true",
                        help="use NetworKit-based estimator for large networks")
    args = parser.parse_args()

    estimator_script = "estimate_properties_networkit.py" if args.networkit else "estimate_properties.py"
    run_estimator(estimator_script, args.n, args.c)

    stats_path = stats_path_from_clustering(args.c)
    if not os.path.exists(stats_path):
        raise SystemExit(f"Expected stats file was not created: {stats_path}")

    run_lfr(stats_path, args.lp, args.cm)


if __name__ == "__main__":
    main()
