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


def print_summary(kinds, totals):
    print()
    print("------------------")
    print("Summary")
    print("------------------")
    for k in sorted(kinds.keys()):
        print(f"{k}: {kinds[k]}")
    print("------------------")
    print("Totals")
    print("------------------")
    for k2 in sorted(totals.keys()):
        print(f"{k2}: {totals[k2]}")


def set_logger(verbose):
    global logger
    log_format_simple = "%(levelname)s %(message)s"
    log_format_complete = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(funcName)s(): %(message)s"
    log_formatter_simple = logging.Formatter(
        log_format_simple, datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter_simple)
    logger = logging.getLogger("helm-resources")
    logger.setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    if verbose == 1:
        logger.setLevel(level=logging.INFO)
    elif verbose > 1:
        log_formatter = logging.Formatter(
            log_format_complete, datefmt="%Y-%m-%dT%H:%M:%S"
        )
        handler.setFormatter(log_formatter)
        logger.setLevel(level=logging.DEBUG)


MULTIPLIER = {
    "m": 1000,
    "Mi": 1024,
}


def extract_number(metric, sep):
    if metric == "-":
        return 0
    elif metric.endswith(sep):
        logger.info(metric)
        return int(metric.split(sep)[0])
    else:
        logger.info(metric)
        return int(MULTIPLIER[sep] * metric)


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
    parser.add_argument(
        "--summary", default=False, action="store_true", help="print summary of objects"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase output verbosity"
    )
    args = parser.parse_args()

    set_logger(args.verbose)

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
    total_cpu_req = 0
    total_cpu_limits = 0
    total_mem_req = 0
    total_mem_limits = 0
    min_servers = 0

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
        # Get name
        name = manifest.get("metadata", {}).get("name", "-")
        logger.info(f"Name: {name}")
        if kind in {"Deployment", "StatefulSet"}:
            # Get replicas
            replicas = manifest.get("spec", {}).get("replicas")
            if not replicas:
                replicas = 1
                replicas_str = "1 (auto)"
            else:
                replicas_str = str(replicas)
            logger.info(f"Replicas: {replicas}")
            containers = (
                manifest.get("spec", {})
                .get("template", {})
                .get("spec", {})
                .get("containers", [])
            )
            for c in containers:
                # Get container name, cpu, mem
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
                if args.summary:
                    total_cpu_req += extract_number(cpu_req, "m")
                    total_cpu_limits += extract_number(cpu_limits, "m")
                    total_mem_req += extract_number(mem_req, "Mi")
                    total_mem_limits += extract_number(mem_limits, "Mi")
                    min_servers = max(min_servers, replicas)
                rows.append(
                    [
                        kind,
                        name,
                        replicas_str,
                        c_name,
                        cpu_req,
                        cpu_limits,
                        mem_req,
                        mem_limits,
                    ]
                )

    if args.output == "table":
        print_pretty_table(headers, rows)
    else:
        # if args.output == "csv":
        print_csv(headers, rows)

    if args.summary:
        totals = {
            "total_cpu_req": total_cpu_req,
            "total_cpu_limits": total_cpu_limits,
            "total_mem_req": total_mem_req,
            "total_mem_limits": total_mem_limits,
            "min_servers": min_servers,
        }
        print_summary(kinds, totals)
