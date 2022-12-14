# helm-resources

This program takes as input a set of Kubernetes manifests/templates from a helm chart and retrieves the resources required to deploy it, printing them in a table or CSV format.

## Getting started

```bash
$ ./helm_resources.py -h
 
$ helm repo add apache-airflow https://airflow.apache.org
$ helm repo update
$ helm pull apache-airflow/airflow --version 1.6.0

$ helm template airflow-1.6.0.tgz | ./helm_resources.py

+-------------+-------------------------+----------+-------------------------+--------------+------------+-----------------+---------------+
| Kind        | Name                    | Replicas | Container               | CPU requests | CPU limits | Memory requests | Memory limits |
+-------------+-------------------------+----------+-------------------------+--------------+------------+-----------------+---------------+
| Deployment  | release-name-scheduler  | 1        | scheduler               | -            | -          | -               | -             |
| Deployment  | release-name-scheduler  | 1        | scheduler-log-groomer   | -            | -          | -               | -             |
| Deployment  | release-name-statsd     | 1        | statsd                  | -            | -          | -               | -             |
| Deployment  | release-name-triggerer  | 1        | triggerer               | -            | -          | -               | -             |
| Deployment  | release-name-webserver  | 1        | webserver               | -            | -          | -               | -             |
| StatefulSet | release-name-postgresql | 1        | release-name-postgresql | 250m         | -          | 256Mi           | -             |
| StatefulSet | release-name-redis      | 1 (auto) | redis                   | -            | -          | -               | -             |
| StatefulSet | release-name-worker     | 1        | worker                  | -            | -          | -               | -             |
| StatefulSet | release-name-worker     | 1        | worker-log-groomer      | -            | -          | -               | -             |
+-------------+-------------------------+----------+-------------------------+--------------+------------+-----------------+---------------+

$ helm template airflow-1.6.0.tgz -f values.yaml| ./helm_resources.py -o csv

Kind;Name;Replicas;Container;CPU requests;CPU limits;Memory requests;Memory limits
Deployment;release-name-scheduler;1;scheduler;-;-;-;-
Deployment;release-name-scheduler;1;scheduler-log-groomer;-;-;-;-
Deployment;release-name-statsd;1;statsd;-;-;-;-
Deployment;release-name-triggerer;1;triggerer;-;-;-;-
Deployment;release-name-webserver;1;webserver;-;-;-;-
StatefulSet;release-name-postgresql;1;release-name-postgresql;250m;-;256Mi;-
StatefulSet;release-name-redis;1 (auto);redis;-;-;-;-
StatefulSet;release-name-worker;1;worker;-;-;-;-
StatefulSet;release-name-worker;1;worker-log-groomer;-;-;-;-

```

And to get an additional summary with the different kinds and the total amount of resources:

```
$ helm template kube-prometheus-stack-42.2.1.tgz |./helm_resources.py --summary
+------------+---------------------------------------+------------+------------------------+--------------+------------+-----------------+---------------+
| Kind       | Name                                  | Replicas   | Container              | CPU requests | CPU limits | Memory requests | Memory limits |
+------------+---------------------------------------+------------+------------------------+--------------+------------+-----------------+---------------+
| DaemonSet  | release-name-prometheus-node-exporter | N/A (auto) | node-exporter          | -            | -          | -               | -             |
| Deployment | release-name-grafana                  | 1          | grafana-sc-dashboard   | -            | -          | -               | -             |
| Deployment | release-name-grafana                  | 1          | grafana-sc-datasources | -            | -          | -               | -             |
| Deployment | release-name-grafana                  | 1          | grafana                | -            | -          | -               | -             |
| Deployment | release-name-kube-state-metrics       | 1          | kube-state-metrics     | -            | -          | -               | -             |
| Deployment | release-name-kube-promethe-operator   | 1          | kube-prometheus-stack  | -            | -          | -               | -             |
| Pod        | release-name-grafana-test             | 1 (auto)   | release-name-test      | -            | -          | -               | -             |
+------------+---------------------------------------+------------+------------------------+--------------+------------+-----------------+---------------+

+--------------------------------+--------+
| Kind                           | Number |
+--------------------------------+--------+
| Alertmanager                   | 1      |
| ClusterRole                    | 5      |
| ClusterRoleBinding             | 5      |
| ConfigMap                      | 30     |
| DaemonSet                      | 1      |
| Deployment                     | 3      |
| Job                            | 2      |
| MutatingWebhookConfiguration   | 1      |
| Pod                            | 1      |
| Prometheus                     | 1      |
| PrometheusRule                 | 29     |
| Role                           | 2      |
| RoleBinding                    | 2      |
| Secret                         | 2      |
| Service                        | 11     |
| ServiceAccount                 | 8      |
| ServiceMonitor                 | 13     |
| ValidatingWebhookConfiguration | 1      |
+--------------------------------+--------+
+------------------+---+
| TOTALS           |   |
+------------------+---+
| min_servers      | 1 |
| total_cpu_limits | 0 |
| total_cpu_req    | 0 |
| total_mem_limits | 0 |
| total_mem_req    | 0 |
+------------------+---+
```

## Requirements

- Python3


