# helm-resources

This program takes as input a set of Kubernetes manifests/templates from a helm chart and retrieves the resources required to deploy it, printing them in a table or CSV format.

## Getting started

```bash
./helm_resources.py -h
 
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm pull apache-airflow/airflow --version 1.6.0
helm template airflow-1.6.0.tgz | ./helm_resources.py
helm template airflow-1.6.0.tgz -f values.yaml| ./helm_resources.py -o csv
```

## Requirements

- Python3


