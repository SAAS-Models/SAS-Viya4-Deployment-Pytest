# Setup tunnel
./setup_kubectl_tunnel.sh

# Run shell script tests
./tests/kubectl_basic_tests.sh
./tests/kubectl_sas_components.sh
./tests/kubectl_cas_tests.sh

# Run Python tests
python tests/kubectl_health_checks.py --namespace sas-viya

# Run pytest integration
pytest tests/test_kubectl_integration.py -v
