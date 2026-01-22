#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script.

Tests all directory endpoints with various filter combinations.
Run this from the backend directory:
    python scripts/test_api_endpoints.py
"""

import json
import sys
from pathlib import Path
from typing import Any

import httpx

# Default base URL
BASE_URL = "http://localhost:5173/api/v1"


def print_test(name: str):
    """Print test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")


def print_result(success: bool, message: str = ""):
    """Print test result."""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} {message}")


def test_endpoint(
    method: str,
    path: str,
    expected_status: int = 200,
    params: dict[str, Any] | None = None,
    description: str = "",
) -> tuple[bool, dict | None]:
    """
    Test an API endpoint.
    
    Returns (success, response_data)
    """
    url = f"{BASE_URL}{path}"
    
    try:
        if method.upper() == "GET":
            response = httpx.get(url, params=params, timeout=10.0)
        else:
            response = httpx.request(method, url, json=params, timeout=10.0)
        
        success = response.status_code == expected_status
        
        try:
            data = response.json() if response.content else None
        except Exception:
            data = {"raw": response.text}
        
        if not success:
            print_result(False, f"Expected {expected_status}, got {response.status_code}")
            if data:
                print(f"  Response: {json.dumps(data, indent=2)}")
        
        return success, data
    
    except httpx.ConnectError:
        print_result(False, f"Connection error - is the server running at {BASE_URL}?")
        return False, None
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False, None


def test_api_info():
    """Test API info endpoint."""
    print_test("API Info Endpoint")
    success, data = test_endpoint("GET", "/")
    
    if success and data:
        print_result(True, "API info endpoint works")
        print(f"  API Version: {data.get('api_version')}")
        print(f"  App Version: {data.get('app_version')}")
        print(f"  Environment: {data.get('environment')}")
        return True
    return False


def test_health_check():
    """Test health check endpoint."""
    print_test("Health Check Endpoint")
    success, data = test_endpoint("GET", "/health")
    
    if success and data:
        print_result(True, "Health check endpoint works")
        print(f"  Status: {data.get('status')}")
        return True
    return False


def test_list_servers_basic():
    """Test basic server listing."""
    print_test("List Servers - Basic (No Filters)")
    success, data = test_endpoint("GET", "/directory/servers")
    
    if success and data:
        servers = data.get("data", [])
        total = data.get("total", 0)
        print_result(True, f"Retrieved {len(servers)} servers (total: {total})")
        
        # Verify response structure
        assert "data" in data, "Missing 'data' field"
        assert "total" in data, "Missing 'total' field"
        assert "page" in data, "Missing 'page' field"
        assert "page_size" in data, "Missing 'page_size' field"
        assert "rank_by" in data, "Missing 'rank_by' field"
        
        # Verify server structure
        if servers:
            server = servers[0]
            required_fields = ["id", "name", "effective_status", "created_at", "updated_at"]
            for field in required_fields:
                assert field in server, f"Server missing required field: {field}"
            
            # Verify mod_list and platforms are lists, not None
            assert isinstance(server.get("mod_list"), list), "mod_list must be a list"
            assert isinstance(server.get("platforms"), list), "platforms must be a list"
            
            # Verify rank fields
            assert "rank_position" in server, "Missing rank_position"
            assert "rank_by" in server, "Missing rank_by in server"
            
            print_result(True, "Response structure is correct")
            print(f"  First server: {server.get('name')}")
            print(f"  Rank by: {data.get('rank_by')}")
        
        return True
    return False


def test_list_servers_pagination():
    """Test pagination."""
    print_test("List Servers - Pagination")
    
    # Test page 1
    success1, data1 = test_endpoint("GET", "/directory/servers", params={"page": 1, "page_size": 2})
    
    if success1 and data1:
        servers1 = data1.get("data", [])
        print_result(True, f"Page 1: {len(servers1)} servers")
        
        # Test page 2
        success2, data2 = test_endpoint("GET", "/directory/servers", params={"page": 2, "page_size": 2})
        
        if success2 and data2:
            servers2 = data2.get("data", [])
            print_result(True, f"Page 2: {len(servers2)} servers")
            
            # Verify different results
            if servers1 and servers2:
                ids1 = {s["id"] for s in servers1}
                ids2 = {s["id"] for s in servers2}
                assert ids1 != ids2, "Page 1 and Page 2 should have different servers"
                print_result(True, "Pagination returns different results")
                return True
    
    return False


def test_list_servers_filters():
    """Test various filters."""
    print_test("List Servers - Filters")
    
    filters_to_test = [
        ("ruleset", {"ruleset": "vanilla"}, "Filter by ruleset=vanilla"),
        ("game_mode", {"game_mode": "pvp"}, "Filter by game_mode=pvp"),
        ("status", {"status": "online"}, "Filter by status=online"),
        ("mode", {"mode": "verified"}, "Filter by mode=verified"),
        ("platforms", {"platforms": ["steam"]}, "Filter by platforms=steam"),
        ("modded", {"modded": "true"}, "Filter modded=true"),
        ("modded", {"modded": "false"}, "Filter modded=false"),
        ("crossplay", {"crossplay": "true"}, "Filter crossplay=true"),
        ("players_min", {"players_current_min": 30}, "Filter players_current_min=30"),
        ("quality_min", {"quality_min": 80.0}, "Filter quality_min=80"),
    ]
    
    all_passed = True
    for filter_name, params, description in filters_to_test:
        success, data = test_endpoint("GET", "/directory/servers", params=params)
        if success and data:
            count = len(data.get("data", []))
            print_result(True, f"{description}: {count} results")
        else:
            print_result(False, f"{description}: Failed")
            all_passed = False
    
    return all_passed


def test_list_servers_search():
    """Test search functionality."""
    print_test("List Servers - Search")
    
    success, data = test_endpoint("GET", "/directory/servers", params={"q": "Island"})
    
    if success and data:
        servers = data.get("data", [])
        print_result(True, f"Search 'Island': {len(servers)} results")
        
        # Verify search results contain "Island"
        if servers:
            found = False
            for server in servers:
                name = server.get("name", "").lower()
                desc = server.get("description", "").lower()
                map_name = server.get("map_name", "").lower()
                if "island" in name or "island" in desc or "island" in map_name:
                    found = True
                    break
            if found:
                print_result(True, "Search results contain 'Island'")
            else:
                print_result(False, "Search results don't contain 'Island'")
                return False
        
        return True
    return False


def test_list_servers_sorting():
    """Test sorting."""
    print_test("List Servers - Sorting")
    
    # Test ascending order
    success1, data1 = test_endpoint("GET", "/directory/servers", params={"order": "asc", "page_size": 5})
    
    if success1 and data1:
        servers1 = data1.get("data", [])
        
        # Test descending order
        success2, data2 = test_endpoint("GET", "/directory/servers", params={"order": "desc", "page_size": 5})
        
        if success2 and data2:
            servers2 = data2.get("data", [])
            
            if len(servers1) >= 2 and len(servers2) >= 2:
                # Verify order is different
                ids1 = [s["id"] for s in servers1]
                ids2 = [s["id"] for s in servers2]
                
                if ids1 != ids2:
                    print_result(True, "Ascending and descending return different orders")
                    return True
                else:
                    print_result(False, "Ascending and descending return same order")
                    return False
    
    return False


def test_get_server():
    """Test get single server."""
    print_test("Get Single Server")
    
    # First, get a server ID from the list
    success_list, data_list = test_endpoint("GET", "/directory/servers", params={"page_size": 1})
    
    if success_list and data_list:
        servers = data_list.get("data", [])
        if servers:
            server_id = servers[0]["id"]
            
            # Test get server by ID
            success, data = test_endpoint("GET", f"/directory/servers/{server_id}")
            
            if success and data:
                print_result(True, f"Retrieved server: {data.get('name')}")
                
                # Verify structure
                assert "id" in data, "Missing 'id' field"
                assert data["id"] == server_id, "Returned wrong server"
                assert "rank_by" in data, "Missing 'rank_by' field"
                
                # Verify mod_list and platforms are lists
                assert isinstance(data.get("mod_list"), list), "mod_list must be a list"
                assert isinstance(data.get("platforms"), list), "platforms must be a list"
                
                print_result(True, "Server structure is correct")
                return True
            else:
                print_result(False, "Failed to retrieve server")
                return False
        else:
            print_result(False, "No servers available to test")
            return False
    
    return False


def test_get_server_not_found():
    """Test get non-existent server."""
    print_test("Get Server - Not Found")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    success, data = test_endpoint("GET", f"/directory/servers/{fake_id}", expected_status=404)
    
    if success:
        print_result(True, "Correctly returns 404 for non-existent server")
        return True
    else:
        print_result(False, "Should return 404 for non-existent server")
        return False


def test_get_filters():
    """Test get filters endpoint."""
    print_test("Get Filters")
    
    success, data = test_endpoint("GET", "/directory/filters")
    
    if success and data:
        print_result(True, "Filters endpoint works")
        
        # Verify structure
        assert "rank_by" in data, "Missing 'rank_by' field"
        assert "rulesets" in data, "Missing 'rulesets' field"
        assert "game_modes" in data, "Missing 'game_modes' field"
        assert "statuses" in data, "Missing 'statuses' field"
        assert "maps" in data, "Missing 'maps' field"
        assert "clusters" in data, "Missing 'clusters' field"
        assert "ranges" in data, "Missing 'ranges' field"
        
        print(f"  Available rulesets: {data.get('rulesets')}")
        print(f"  Available game_modes: {data.get('game_modes')}")
        print(f"  Available maps: {len(data.get('maps', []))} maps")
        
        print_result(True, "Filters structure is correct")
        return True
    
    return False


def test_complex_filters():
    """Test complex filter combinations."""
    print_test("List Servers - Complex Filter Combinations")
    
    complex_filters = [
        ({"ruleset": "vanilla", "game_mode": "pvp"}, "ruleset=vanilla AND game_mode=pvp"),
        ({"platforms": ["steam", "epic"], "modded": "false"}, "platforms=steam,epic AND modded=false"),
        ({"players_current_min": 30, "quality_min": 80.0}, "players>=30 AND quality>=80"),
        ({"ruleset": "modded", "modded": "true"}, "ruleset=modded AND modded=true"),
    ]
    
    all_passed = True
    for params, description in complex_filters:
        success, data = test_endpoint("GET", "/directory/servers", params=params)
        if success and data:
            count = len(data.get("data", []))
            print_result(True, f"{description}: {count} results")
        else:
            print_result(False, f"{description}: Failed")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("="*60)
    print("API ENDPOINT TEST SUITE")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print("\nMake sure your server is running!")
    print("  cd backend && python -m uvicorn app.main:app --reload --port 5173")
    
    results = []
    
    # Basic endpoints
    results.append(("API Info", test_api_info()))
    results.append(("Health Check", test_health_check()))
    
    # Directory endpoints
    results.append(("List Servers - Basic", test_list_servers_basic()))
    results.append(("List Servers - Pagination", test_list_servers_pagination()))
    results.append(("List Servers - Filters", test_list_servers_filters()))
    results.append(("List Servers - Search", test_list_servers_search()))
    results.append(("List Servers - Sorting", test_list_servers_sorting()))
    results.append(("List Servers - Complex Filters", test_complex_filters()))
    results.append(("Get Server", test_get_server()))
    results.append(("Get Server - Not Found", test_get_server_not_found()))
    results.append(("Get Filters", test_get_filters()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
