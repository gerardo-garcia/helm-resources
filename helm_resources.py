#!/usr/bin/python3

# helm template | helm_resources.py

import yaml
import sys
import argparse
from prettytable import PrettyTable
import logging

####################################
# Global functions
####################################
deployments = {}
daemonsets = {}
replicasets = {}
sts = {}
hpas = {}
pods = {}

def print_pretty_table(headers, rows):
    table = PrettyTable(headers)
    for row in rows:
        table.add_row(row)
    table.align = "l"
    print(table)

def print_csv(headers, rows):
    print(";".join(headers))
    for row in rows:
        str_row = list(map(str, row))
        print(";".join(str_row))

def print_kinds(kinds):
    for k in sorted(kinds.keys()):
        print(f"{k}: {kinds[k]}")

def set_logger(verbose):
    global logger
    log_format_simple = "%(levelname)s %(message)s"
    log_format_complete = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(funcName)s(): %(message)s"
    log_formatter_simple = logging.Formatter(log_format_simple, datefmt='%Y-%m-%dT%H:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter_simple)
    logger = logging.getLogger('helm-resources')
    logger.setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    if verbose==1:
        logger.setLevel(level=logging.INFO)
    elif verbose>1:
        log_formatter = logging.Formatter(log_format_complete, datefmt='%Y-%m-%dT%H:%M:%S')
        handler.setFormatter(log_formatter)
        logger.setLevel(level=logging.DEBUG)

####################################
# Global variables
####################################
deployments = {}
daemonsets = {}
replicasets = {}
sts = {}
hpas = {}
pods = {}
relevant_kinds = {"Deployment", "StatefulSet", "Pod", "HorizontalPodAutoscaler", "ReplicaSet", "DaemonSet"}
kinds = {}

####################################
# Main
####################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output",
                        choices=["table", "csv"],
                        default="table",
                        help="output format")
    parser.add_argument("--summary",
                        default=False,
                        action="store_true",
                        help="print summary of objects")
    parser.add_argument("-v", "--verbose",
                        action="count",
                        default=0,
                        help="increase output verbosity")
    args = parser.parse_args()

    set_logger(args.verbose)
    headers = ["Kind", "Name", "Replicas", "Container", "CPU requests", "CPU limits", "Memory requests", "Memory limits"]
    rows = []

    # Read Manifests and store info in global dicts
    manifest_generator = yaml.safe_load_all(sys.stdin)
    for manifest in manifest_generator:
        if not manifest:
            logger.info("Empty manifest")
            continue
        logger.debug(f"{manifest}")
        kind = manifest.get("kind", "None")
        logger.info(f"Kind: {kind}")
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind not in relevant_kinds:
            continue
        name = manifest.get("metadata", {}).get("name", "-")
        logger.info(f"Name: {name}")
        if kind in {"Deployment", "StatefulSet"}:
            replicas = manifest.get("spec", {}).get("replicas", "1 (auto)")
            logger.info(f"Replicas: {replicas}")
            containers = manifest.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
            for c in containers:
                c_name = c.get("name", "-")
                logger.info(f"Container name: {c_name}")
                c_resources = c.get("resources", {})
                logger.info(f"Container resources: {yaml.safe_dump(c_resources)}")
                c_req = c_resources.get("requests", {})
                c_limits = c_resources.get("limits", {})
                cpu_req = c_req.get("cpu", "-")
                cpu_limits = c_limits.get("cpu", "-")
                mem_req = c_req.get("memory", "-")
                mem_limits = c_limits.get("memory", "-")
                rows.append([kind, name, replicas, c_name, cpu_req, cpu_limits, mem_req, mem_limits])
        # rows.append([kind, name])

    if args.output == "table":
        print_pretty_table(headers, rows)
    else:
        # if args.output == "csv":
        print_csv(headers, rows)

    if args.summary:
        print_summary(kinds)
