#!/usr/bin/env python3

import subprocess
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class SASViyaKubectlTester:
    def __init__(self, namespace: str = "sas-viya"):
        self.namespace = namespace
        self.test_results = []
        
    def run_kubectl(self, command: str) -> Tuple[bool, str]:
        """Execute kubectl command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def test_pod_health(self) -> Dict:
        """Test all pods health in namespace"""
        print(f"\n{'='*50}")
        print("Testing Pod Health")
        print('='*50)
        
        cmd = f"kubectl get pods -n {self.namespace} -o json"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            return {"status": "FAILED", "error": "Cannot get pods"}
        
        pods = json.loads(output)
        pod_status = {
            "total": 0,
            "running": 0,
            "pending": 0,
            "failed": 0,
            "unknown": 0,
            "problematic_pods": []
        }
        
        for pod in pods.get('items', []):
            pod_name = pod['metadata']['name']
            phase = pod['status']['phase']
            pod_status['total'] += 1
            
            if phase == 'Running':
                # Check if all containers are ready
                all_ready = all(
                    c.get('ready', False) 
                    for c in pod['status'].get('containerStatuses', [])
                )
                if all_ready:
                    pod_status['running'] += 1
                else:
                    pod_status['problematic_pods'].append({
                        'name': pod_name,
                        'issue': 'Containers not ready'
                    })
            elif phase == 'Pending':
                pod_status['pending'] += 1
                pod_status['problematic_pods'].append({
                    'name': pod_name,
                    'issue': 'Pod pending'
                })
            elif phase == 'Failed':
                pod_status['failed'] += 1
                pod_status['problematic_pods'].append({
                    'name': pod_name,
                    'issue': 'Pod failed'
                })
            else:
                pod_status['unknown'] += 1
        
        # Print summary
        print(f"Total Pods: {pod_status['total']}")
        print(f"Running: {pod_status['running']}")
        print(f"Pending: {pod_status['pending']}")
        print(f"Failed: {pod_status['failed']}")
        
        if pod_status['problematic_pods']:
            print("\n⚠ Problematic Pods:")
            for pod in pod_status['problematic_pods'][:5]:  # Show first 5
                print(f"  - {pod['name']}: {pod['issue']}")
        
        test_passed = pod_status['failed'] == 0 and pod_status['pending'] == 0
        self.test_results.append({
            'test': 'Pod Health',
            'passed': test_passed,
            'details': pod_status
        })
        
        return pod_status
    
    def test_persistent_volumes(self) -> Dict:
        """Test PVC status"""
        print(f"\n{'='*50}")
        print("Testing Persistent Volume Claims")
        print('='*50)
        
        cmd = f"kubectl get pvc -n {self.namespace} -o json"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            return {"status": "FAILED", "error": "Cannot get PVCs"}
        
        pvcs = json.loads(output)
        pvc_status = {
            "total": 0,
            "bound": 0,
            "pending": 0,
            "lost": 0,
            "issues": []
        }
        
        for pvc in pvcs.get('items', []):
            pvc_name = pvc['metadata']['name']
            phase = pvc['status'].get('phase', 'Unknown')
            pvc_status['total'] += 1
            
            if phase == 'Bound':
                pvc_status['bound'] += 1
            elif phase == 'Pending':
                pvc_status['pending'] += 1
                pvc_status['issues'].append(f"{pvc_name}: Pending")
            elif phase == 'Lost':
                pvc_status['lost'] += 1
                pvc_status['issues'].append(f"{pvc_name}: Lost")
        
        print(f"Total PVCs: {pvc_status['total']}")
        print(f"Bound: {pvc_status['bound']}")
        print(f"Pending: {pvc_status['pending']}")
        print(f"Lost: {pvc_status['lost']}")
        
        if pvc_status['issues']:
            print("\n⚠ PVC Issues:")
            for issue in pvc_status['issues']:
                print(f"  - {issue}")
        
        test_passed = pvc_status['pending'] == 0 and pvc_status['lost'] == 0
        self.test_results.append({
            'test': 'Persistent Volumes',
            'passed': test_passed,
            'details': pvc_status
        })
        
        return pvc_status
    
    def test_services(self) -> Dict:
        """Test service endpoints"""
        print(f"\n{'='*50}")
        print("Testing Services")
        print('='*50)
        
        cmd = f"kubectl get services -n {self.namespace} -o json"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            return {"status": "FAILED", "error": "Cannot get services"}
        
        services = json.loads(output)
        critical_services = [
            'sas-logon-app',
            'sas-cas-server',
            'sas-postgres',
            'sas-rabbitmq-server',
            'sas-consul-server'
        ]
        
        service_status = {
            "total": 0,
            "with_endpoints": 0,
            "without_endpoints": 0,
            "critical_missing": [],
            "all_services": []
        }
        
        for service in services.get('items', []):
            service_name = service['metadata']['name']
            service_status['total'] += 1
            service_status['all_services'].append(service_name)
            
            # Check endpoints
            cmd = f"kubectl get endpoints {service_name} -n {self.namespace} -o json"
            ep_success, ep_output = self.run_kubectl(cmd)
            
            if ep_success:
                endpoints = json.loads(ep_output)
                subsets = endpoints.get('subsets', [])
                if subsets and any(s.get('addresses') for s in subsets):
                    service_status['with_endpoints'] += 1
                else:
                    service_status['without_endpoints'] += 1
                    
                    # Check if it's a critical service
                    for critical in critical_services:
                        if critical in service_name:
                            service_status['critical_missing'].append(service_name)
        
        print(f"Total Services: {service_status['total']}")
        print(f"With Endpoints: {service_status['with_endpoints']}")
        print(f"Without Endpoints: {service_status['without_endpoints']}")
        
        if service_status['critical_missing']:
            print("\n⚠ Critical Services Missing Endpoints:")
            for service in service_status['critical_missing']:
                print(f"  - {service}")
        
        test_passed = len(service_status['critical_missing']) == 0
        self.test_results.append({
            'test': 'Services',
            'passed': test_passed,
            'details': service_status
        })
        
        return service_status
    
    def test_ingress(self) -> Dict:
        """Test ingress configuration"""
        print(f"\n{'='*50}")
        print("Testing Ingress")
        print('='*50)
        
        cmd = f"kubectl get ingress -n {self.namespace} -o json"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            print("No ingress found or cannot get ingress")
            return {"status": "No ingress configured"}
        
        ingresses = json.loads(output)
        ingress_status = {
            "total": 0,
            "with_address": 0,
            "rules": [],
            "hosts": []
        }
        
        for ingress in ingresses.get('items', []):
            ingress_name = ingress['metadata']['name']
            ingress_status['total'] += 1
            
            # Check if ingress has address
            lb_ingress = ingress.get('status', {}).get('loadBalancer', {}).get('ingress', [])
            if lb_ingress:
                ingress_status['with_address'] += 1
                
            # Get rules
            rules = ingress.get('spec', {}).get('rules', [])
            for rule in rules:
                host = rule.get('host', '*')
                ingress_status['hosts'].append(host)
                print(f"  Host: {host}")
                
                http_rules = rule.get('http', {}).get('paths', [])
                for path_rule in http_rules:
                    path = path_rule.get('path', '/')
                    backend = path_rule.get('backend', {})
                    service = backend.get('service', {}).get('name', 'unknown')
                    print(f"    Path: {path} -> Service: {service}")
        
        test_passed = ingress_status['with_address'] > 0 if ingress_status['total'] > 0 else True
        self.test_results.append({
            'test': 'Ingress',
            'passed': test_passed,
            'details': ingress_status
        })
        
        return ingress_status
    
    def test_resource_usage(self) -> Dict:
        """Test resource usage"""
        print(f"\n{'='*50}")
        print("Testing Resource Usage")
        print('='*50)
        
        # Get node metrics
        cmd = "kubectl top nodes --no-headers"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            print("Metrics server not available")
            return {"status": "Metrics not available"}
        
        print("Node Resource Usage:")
        print(output)
        
        # Get pod metrics for namespace
        cmd = f"kubectl top pods -n {self.namespace} --no-headers | head -10"
        success, output = self.run_kubectl(cmd)
        
        if success:
            print(f"\nTop 10 Pods Resource Usage in {self.namespace}:")
            print(output)
        
        return {"status": "Completed"}
    
    def test_recent_events(self) -> Dict:
        """Check for recent warning events"""
        print(f"\n{'='*50}")
        print("Checking Recent Events")
        print('='*50)
        
        cmd = f"kubectl get events -n {self.namespace} --field-selector type=Warning -o json"
        success, output = self.run_kubectl(cmd)
        
        if not success:
            return {"status": "FAILED", "error": "Cannot get events"}
        
        events = json.loads(output)
        warning_events = []
        
        for event in events.get('items', [])[-10:]:  # Last 10 warnings
            warning_events.append({
                'object': event.get('involvedObject', {}).get('name', 'unknown'),
                'reason': event.get('reason', 'unknown'),
                'message': event.get('message', 'no message'),
                'count': event.get('count', 1)
            })
        
        if warning_events:
            print(f"Found {len(warning_events)} recent warning events:")
            for event in warning_events[:5]:  # Show first 5
                print(f"  - {event['object']}: {event['reason']} ({event['count']} times)")
                print(f"    {event['message'][:100]}...")
        else:
            print("No recent warning events")
        
        return {"warnings": warning_events}
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("SAS VIYA KUBECTL VALIDATION TESTS")
        print("="*60)
        print(f"Namespace: {self.namespace}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all tests
        self.test_pod_health()
        self.test_persistent_volumes()
        self.test_services()
        self.test_ingress()
        self.test_resource_usage()
        self.test_recent_events()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        failed = sum(1 for t in self.test_results if not t['passed'])
        
        for test in self.test_results:
            status = "✓ PASSED" if test['passed'] else "✗ FAILED"
            print(f"{test['test']}: {status}")
        
        print(f"\nTotal: {passed} passed, {failed} failed")
        
        return failed == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SAS Viya deployment using kubectl')
    parser.add_argument('--namespace', default='sas-viya', help='Kubernetes namespace')
    args = parser.parse_args()
    
    tester = SASViyaKubectlTester(namespace=args.namespace)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
