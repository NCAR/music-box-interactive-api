import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_chapman_example_api(api_client):
    url = reverse('set-example')  
    params = {'example': "CHAPMAN"}  
    
    response = api_client.get(url, params)
    
    assert response.status_code == 200
    #assert response.data == [{"id": 1, "name": "Example"}] "FLOW_TUBE" "FULL_GAS_PHASE"

"""
@pytest.mark.django_db
def test_flow_tube_example_api(api_client):
    url = reverse('set-example')  
    params = {'example': "FLOW_TUBE" }  
    
    response = api_client.get(url, params)
    
    assert response.status_code == 200
 
 
@pytest.mark.django_db
def test_full_gas_phase_example_api(api_client):
    url = reverse('set-example')  
    params = {'example': "FULL_GAS_PHASE"}  
    
    response = api_client.get(url, params)
    
    assert response.status_code == 200
"""