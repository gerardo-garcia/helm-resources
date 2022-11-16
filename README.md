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

## Requirements

- Python3


