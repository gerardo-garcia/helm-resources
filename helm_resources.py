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


def print_table(headers, rows, output_format):
    if output_format == "table":
        print_pretty_table(headers, rows)
    else:
        # if output_format == "csv":
        print_csv(headers, rows)


def print_summary(kinds, totals):
    print()
    table = PrettyTable(["Kind", "Number"])
    for k, v in sorted(kinds.items()):
        table.add_row([k, v])
    table.align = "l"
    print(table)

    table2 = PrettyTable(["TOTALS", ""])
    for k, v in sorted(totals.items()):
        table2.add_row([k, v])
    table2.align = "l"
    print(table2)


def set_logger(verbose):
    global logger
    log_format_simple = "%(levelname)s %(message)s"
    log_format_complete = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(funcName)s(): %(message)s"
    log_formatter_simple = logging.Formatter(log_format_simple, datefmt="%Y-%m-%dT%H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter_simple)
    logger = logging.getLogger("helm-resources")
    logger.setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    if verbose == 1:
        logger.setLevel(level=logging.INFO)
    elif verbose > 1:
        log_formatter = logging.Formatter(log_format_complete, datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(log_formatter)
        logger.setLevel(level=logging.DEBUG)


MULTIPLIER = {
    "m": 1000,
    "Mi": 1024,
}


def extract_number(metric, sep):
    metric_str = str(metric)
    if metric_str == "-":
        return 0
    elif metric_str.endswith(sep):
        logger.info(metric)
        return int(metric.split(sep)[0])
    else:
        logger.info(metric)
        return int(MULTIPLIER[sep] * metric)


def get_manifest_params(manifest, kinds):
    logger.debug(f"{manifest}")
    # Get kind
    kind = manifest.get("kind", "None")
    logger.info(f"Kind: {kind}")
    kinds[kind] = kinds.get(kind, 0) + 1
    # Get name
    name = manifest.get("metadata", {}).get("name", "-")
    logger.info(f"Name: {name}")
    return kind, name


def get_replicas(manifest, kind):
    # Get replicas, replicas_str
    if kind in {"DaemonSet"}:
        replicas = 1
        replicas_str = "N/A (auto)"
    elif kind in {"Pod"}:
        replicas = 1
        replicas_str = "1 (auto)"
    elif kind in {"Deployment", "StatefulSet", "ReplicaSet"}:
        replicas = manifest.get("spec", {}).get("replicas")
        if not replicas:
            replicas = 1
            replicas_str = "1 (auto)"
        else:
            replicas_str = str(replicas)
        logger.info(f"Replicas: {replicas}")
    return replicas, replicas_str


def get_containers(manifest, kind):
    if kind != "Pod":
        containers = manifest.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    else:
        containers = manifest.get("spec", {}).get("containers", [])
    return containers


def get_container_params(container):
    # Get container name, cpu req and limits, mem req and limits
    c_name = container.get("name", "-")
    logger.info(f"Container name: {c_name}")
    c_resources = container.get("resources", {})
    logger.info(f"Container resources: {yaml.safe_dump(c_resources)}")
    if not c_resources:
        c_resources = {}
    c_req = c_resources.get("requests", {})
    c_limits = c_resources.get("limits", {})
    cpu_req = c_req.get("cpu", "-")
    cpu_limits = c_limits.get("cpu", "-")
    mem_req = c_req.get("memory", "-")
    mem_limits = c_limits.get("memory", "-")
    return c_name, cpu_req, cpu_limits, mem_req, mem_limits


def get_hpa_info(manifest, hpas):
    spec = manifest.get("spec", {})
    # spec.scaleTargetRef
    # spec.minReplicas
    # spec.maxReplicas
    return


def update_totals(totals, cpu_req, cpu_limits, mem_req, mem_limits, replicas):
    totals["total_cpu_req"] += extract_number(cpu_req, "m")
    totals["total_cpu_limits"] += extract_number(cpu_limits, "m")
    totals["total_mem_req"] += extract_number(mem_req, "Mi")
    totals["total_mem_limits"] += extract_number(mem_limits, "Mi")
    totals["min_servers"] = max(totals["min_servers"], replicas)
    return


####################################
# Global variables
####################################
deployments = {}
daemonsets = {}
replicasets = {}
sts = {}
hpas = {}
pods = {}
relevant_kinds = {
    "Deployment",
    "StatefulSet",
    "Pod",
    "HorizontalPodAutoscaler",
    "ReplicaSet",
    "DaemonSet",
}
kinds = {}


####################################
# Main
####################################
if __name__ == "__main__":
    # Argument parse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        choices=["table", "csv"],
        default="table",
        help="output format",
    )
    parser.add_argument("--summary", default=False, action="store_true", help="print summary of objects")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger
    set_logger(args.verbose)

    # Initialize variables
    headers = [
        "Kind",
        "Name",
        "Replicas",
        "Container",
        "CPU requests",
        "CPU limits",
        "Memory requests",
        "Memory limits",
    ]
    rows = []
    totals = {
        "total_cpu_req": 0,
        "total_cpu_limits": 0,
        "total_mem_req": 0,
        "total_mem_limits": 0,
        "min_servers": 0,
    }

    # Read Manifests and get container params
    manifest_generator = yaml.safe_load_all(sys.stdin)
    for manifest in manifest_generator:
        if not manifest:
            logger.info("Empty manifest")
            continue
        kind, name = get_manifest_params(manifest, kinds)
        if kind not in relevant_kinds:
            continue
        if kind in {"HorizontalPodAutoscaler"}:
            continue
        replicas, replicas_str = get_replicas(manifest, kind)
        containers = get_containers(manifest, kind)
        for c in containers:
            # Get container params
            c_name, cpu_req, cpu_limits, mem_req, mem_limits = get_container_params(c)
            # Update totals
            if args.summary:
                update_totals(totals, cpu_req, cpu_limits, mem_req, mem_limits, replicas)
            # Update table
            rows.append([kind, name, replicas_str, c_name, cpu_req, cpu_limits, mem_req, mem_limits])
    print_table(headers, rows, args.output)
    if args.summary:
        print_summary(kinds, totals)
