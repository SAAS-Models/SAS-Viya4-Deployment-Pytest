#!/bin/bash

# Configuration
BASTION_USER="ec2-user"
BASTION_HOST="bastion.example.com"
BASTION_KEY="/path/to/bastion-key.pem"
K8S_API_INTERNAL="k8s-api.internal.example.com"
LOCAL_PORT=6443

# Create SSH tunnel for Kubernetes API
echo "Creating SSH tunnel for Kubernetes API..."
ssh -i ${BASTION_KEY} \
    -L ${LOCAL_PORT}:${K8S_API_INTERNAL}:443 \
    -N -f ${BASTION_USER}@${BASTION_HOST}

# Update kubeconfig to use tunnel
kubectl config set-cluster eks-cluster \
    --server=https://localhost:${LOCAL_PORT} \
    --insecure-skip-tls-verify=true

kubectl config set-context sas-viya-context \
    --cluster=eks-cluster \
    --user=aws-user \
    --namespace=sas-viya

kubectl config use-context sas-viya-context

echo "kubectl configured to use tunnel on localhost:${LOCAL_PORT}"

# Test connection
kubectl cluster-info
