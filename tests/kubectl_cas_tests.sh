#!/bin/bash

NAMESPACE="sas-viya"

echo "======================================="
echo "CAS Server Validation Tests"
echo "======================================="

# 1. Check CAS Controller
echo "1. CAS Controller Status:"
kubectl get pods -n ${NAMESPACE} \
    -l "app.kubernetes.io/name=sas-cas-server-default-controller" \
    -o wide

# 2. Check CAS Workers
echo -e "\n2. CAS Workers:"
kubectl get pods -n ${NAMESPACE} \
    -l "app.kubernetes.io/name=sas-cas-server-default-worker" \
    -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# 3. CAS Service Endpoints
echo -e "\n3. CAS Service Endpoints:"
kubectl get endpoints -n ${NAMESPACE} | grep cas

# 4. CAS ConfigMaps
echo -e "\n4. CAS Configuration:"
kubectl get configmap -n ${NAMESPACE} | grep cas | head -5

# 5. Check CAS PVCs
echo -e "\n5. CAS Persistent Volumes:"
kubectl get pvc -n ${NAMESPACE} | grep cas

# 6. CAS Resource Usage
echo -e "\n6. CAS Resource Usage:"
kubectl top pods -n ${NAMESPACE} | grep cas

# 7. CAS Logs Check
echo -e "\n7. Recent CAS Controller Logs (last 5 lines):"
CAS_POD=$(kubectl get pods -n ${NAMESPACE} \
    -l "app.kubernetes.io/name=sas-cas-server-default-controller" \
    -o jsonpath='{.items[0].metadata.name}')

if [ ! -z "$CAS_POD" ]; then
    kubectl logs -n ${NAMESPACE} ${CAS_POD} --tail=5
fi

# 8. CAS Network Policy
echo -e "\n8. CAS Network Policies:"
kubectl get networkpolicy -n ${NAMESPACE} | grep cas

# 9. CAS AutoScaling
echo -e "\n9. CAS AutoScaling Configuration:"
kubectl get hpa -n ${NAMESPACE} | grep cas || echo "No HPA configured for CAS"
