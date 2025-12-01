import pytest
import subprocess
import json
import yaml

class TestKubectlIntegration:
    
    @pytest.fixture(scope="class")
    def namespace(self):
        return "sas-viya"
    
    def run_kubectl(self, command):
        """Helper to run kubectl commands"""
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    
    @pytest.mark.critical
    def test_namespace_exists(self, namespace):
        """Test if SAS Viya namespace exists"""
        success, stdout, _ = self.run_kubectl(f"kubectl get namespace {namespace}")
        assert success, f"Namespace {namespace} does not exist"
    
    @pytest.mark.critical
    def test_cas_controller_running(self, namespace):
        """Test if CAS controller is running"""
        success, stdout, _ = self.run_kubectl(
            f"kubectl get pods -n {namespace} "
            "-l 'app.kubernetes.io/name=sas-cas-server-default-controller' "
            "-o jsonpath='{.items[0].status.phase}'"
        )
        assert success, "Cannot get CAS controller status"
        assert "Running" in stdout, f"CAS controller is not running. Status: {stdout}"
    
    @pytest.mark.critical
    def test_required_deployments(self, namespace):
        """Test if required deployments are ready"""
        required_deployments = [
            "sas-logon-app",
            "sas-identities",
            "sas-authorization",
            "sas-files",
            "sas-folders"
        ]
        
        for deployment in required_deployments:
            cmd = f"kubectl get deployment {deployment} -n {namespace} -o json"
            success, stdout, _ = self.run_kubectl(cmd)
            
            if success and stdout:
                dep_data = json.loads(stdout)
                ready = dep_data.get('status', {}).get('readyReplicas', 0)
                desired = dep_data.get('spec', {}).get('replicas', 1)
                assert ready == desired, f"{deployment}: {ready}/{desired} replicas ready"
            else:
                pytest.skip(f"Deployment {deployment} not found")
    
    @pytest.mark.services
    def test_service_endpoints(self, namespace):
        """Test if critical services have endpoints"""
        critical_services = [
            "sas-logon-app",
            "sas-cas-server",
            "sas-postgres"
        ]
        
        for service in critical_services:
            cmd = f"kubectl get endpoints {service} -n {namespace} -o json"
            success, stdout, _ = self.run_kubectl(cmd)
            
            assert success, f"Cannot get endpoints for {service}"
            
            endpoints = json.loads(stdout)
            subsets = endpoints.get('subsets', [])
            assert subsets, f"Service {service} has no endpoints"
            assert any(s.get('addresses') for s in subsets), \
                f"Service {service} has no active addresses"
    
    @pytest.mark.slow
    def test_pod_restart_count(self, namespace):
        """Check if any pods have high restart counts"""
        max_restarts = 5
        
        cmd = f"kubectl get pods -n {namespace} -o json"
        success, stdout, _ = self.run_kubectl(cmd)
        
        assert success, "Cannot get pod information"
        
        pods = json.loads(stdout)
        problematic_pods = []
        
        for pod in pods.get('items', []):
            pod_name = pod['metadata']['name']
            for container in pod.get('status', {}).get('containerStatuses', []):
                restart_count = container.get('restartCount', 0)
                if restart_count > max_restarts:
                    problematic_pods.append({
                        'pod': pod_name,
                        'container': container['name'],
                        'restarts': restart_count
                    })
        
        assert not problematic_pods, \
            f"Pods with high restart counts: {problematic_pods}"
    
    @pytest.mark.infrastructure
    def test_persistent_volumes_bound(self, namespace):
        """Test if all PVCs are bound"""
        cmd = f"kubectl get pvc -n {namespace} -o json"
        success, stdout, _ = self.run_kubectl(cmd)
        
        assert success, "Cannot get PVC information"
        
        pvcs = json.loads(stdout)
        unbound_pvcs = []
        
        for pvc in pvcs.get('items', []):
            pvc_name = pvc['metadata']['name']
            phase = pvc.get('status', {}).get('phase', 'Unknown')
            if phase != 'Bound':
                unbound_pvcs.append(f"{pvc_name}: {phase}")
        
        assert not unbound_pvcs, f"Unbound PVCs: {unbound_pvcs}"
