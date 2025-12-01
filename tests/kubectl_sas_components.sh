#!/bin/bash

NAMESPACE="sas-viya"

echo "======================================="
echo "Testing SAS Viya Components"
echo "======================================="

# Function to check deployment status
check_deployment() {
    local deployment=$1
    local label=$2
    
    echo "Checking deployment: ${deployment}"
    
    # Get deployment status
    kubectl get deployment -n ${NAMESPACE} -l "${label}" -o json | \
    jq -r '.items[] | "\(.metadata.name): \(.status.readyReplicas)/\(.spec.replicas)"'
    
    # Check if all replicas are ready
    ready=$(kubectl get deployment -n ${NAMESPACE} -l "${label}" -o json | \
            jq '[.items[].status.conditions[] | select(.type=="Available" and .status=="True")] | length')
    
    total=$(kubectl get deployment -n ${NAMESPACE} -l "${label}" -o json | \
            jq '.items | length')
    
    if [ "$ready" == "$total" ]; then
        echo "✓ All ${deployment} deployments are ready"
    else
        echo "✗ Some ${deployment} deployments are not ready"
        return 1
    fi
    echo ""
}

# Test CAS Server
echo "1. CAS Server Status:"
kubectl get pods -n ${NAMESPACE} -l "app.kubernetes.io/name=sas-cas-server" \
    -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[0].ready

# Test SAS Logon Manager
echo -e "\n2. SAS Logon Manager:"
check_deployment "SAS Logon" "app.kubernetes.io/name=sas-logon-app"

# Test SAS Studio
echo "3. SAS Studio:"
kubectl get pods -n ${NAMESPACE} -l "app=sas-studio-app" \
    -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# Test Microservices
echo -e "\n4. Core Microservices:"
for service in "sas-identities" "sas-authorization" "sas-files" "sas-folders"; do
    status=$(kubectl get deployment -n ${NAMESPACE} ${service} \
             -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null)
    if [ "$status" == "True" ]; then
        echo "✓ ${service}: Available"
    else
        echo "✗ ${service}: Not Available"
    fi
done

# Test PostgreSQL
echo -e "\n5. PostgreSQL Database:"
kubectl get statefulset -n ${NAMESPACE} -l "app.kubernetes.io/name=postgres" \
    -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,REPLICAS:.status.replicas

# Test RabbitMQ
echo -e "\n6. RabbitMQ Message Broker:"
kubectl get pods -n ${NAMESPACE} -l "app=sas-rabbitmq-server" \
    -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[0].ready

# Test Consul
echo -e "\n7. Consul Service Discovery:"
kubectl get pods -n ${NAMESPACE} -l "app=sas-consul-server" --no-headers | wc -l | \
    xargs -I {} echo "Consul instances running: {}"
