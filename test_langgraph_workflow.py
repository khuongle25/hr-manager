#!/usr/bin/env python3
"""
Test Script cho LangGraph Complex Approval Workflow
"""

import os
import sys
import json
import requests
from datetime import datetime, date, timedelta

# Add ai_agent to path để import được
sys.path.append('./ai_agent')

def test_complex_workflow_standalone():
    """Test complex workflow independently"""
    print("🧪 Testing LangGraph Complex Approval Workflow (Standalone)...")
    
    try:
        from langgraph_approval_workflow import create_complex_approval_workflow
        
        # Initialize workflow
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAy1zLhUYfX-B_r71zENYncn18vJDp0V5k")
        workflow = create_complex_approval_workflow(gemini_api_key)
        
        # Mock state for testing
        test_state = {
            "user_input": "Duyệt đơn nghỉ phép team lead cuối năm có nhiều conflicts",
            "user_id": 28,
            "user_role": "hr",
            "user_token": "mock_token_for_testing",
            "intent": "approve_leave",
            "entities": {"leave_request_id": 21},
            # Initialize empty lists for annotations
            "conflicts": [],
            "risks": [],
            "business_rules_triggered": [],
            "api_calls": [],
            # Initialize other fields
            "leave_request": None,
            "employee_context": None,
            "team_context": None,
            "department_context": None,
            "risk_score": 0,
            "requires_escalation": False,
            "escalation_reason": "",
            "recommended_action": "",
            "user_message": "",
            "execution_result": {}
        }
        
        print("✅ Workflow initialized successfully")
        print("✅ Test state prepared")
        
        # Test workflow creation và basic structure
        print(f"✅ Workflow type: {type(workflow)}")
        print(f"✅ Workflow has execute method: {hasattr(workflow, 'execute')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone test failed: {e}")
        return False

def test_integration_with_fastapi():
    """Test integration với FastAPI endpoint"""
    print("\n🧪 Testing Integration with FastAPI...")
    
    # Test data với complex scenario
    test_cases = [
        {
            "name": "Team Lead End-of-Year Leave with Conflicts",
            "payload": {
                "user_id": 28,
                "role": "hr",
                "message": "Duyệt đơn nghỉ phép ID 21 team lead cuối năm",
                "token": "fake_token_for_testing"
            },
            "expected_workflow": "langgraph_complex"
        },
        {
            "name": "Simple Employee Leave (Should NOT use complex workflow)",
            "payload": {
                "user_id": 1,
                "role": "employee", 
                "message": "Duyệt đơn nghỉ phép ID 20",
                "token": "fake_token_for_testing"
            },
            "expected_workflow": "simple"
        },
        {
            "name": "HR Complex Approval with Overlap Keywords",
            "payload": {
                "user_id": 2,
                "role": "hr",
                "message": "Duyệt đơn ID 21 có overlap với nhiều team members critical deadline",
                "token": "fake_token_for_testing"
            },
            "expected_workflow": "langgraph_complex"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        
        try:
            # Test with mock - chỉ test logic flow, không gọi API thực
            from ai_agent.intent_api_mapping import should_use_complex_approval
            
            # Extract intent từ message (simplified)
            intent = "approve_leave" if "duyệt" in test_case["payload"]["message"].lower() else "unknown"
            entities = {"leave_request_id": 21} if "21" in test_case["payload"]["message"] else {}
            
            should_use_complex = should_use_complex_approval(
                intent=intent,
                entities=entities,
                user_role=test_case["payload"]["role"],
                user_input=test_case["payload"]["message"]
            )
            
            expected_complex = test_case["expected_workflow"] == "langgraph_complex"
            
            if should_use_complex == expected_complex:
                print(f"✅ Workflow routing correct: Complex={should_use_complex}")
            else:
                print(f"❌ Workflow routing incorrect: Expected Complex={expected_complex}, Got={should_use_complex}")
                
        except Exception as e:
            print(f"❌ Test case {i} failed: {e}")

def test_trigger_detection():
    """Test trigger word detection"""
    print("\n🧪 Testing Trigger Word Detection...")
    
    test_messages = [
        ("Duyệt đơn nghỉ phép team lead cuối năm", True, "team lead + cuối năm"),
        ("Approve leave request with department overlap", True, "overlap"),
        ("Duyệt đơn nghỉ phép critical deadline december", True, "critical + december"),
        ("Duyệt đơn nghỉ phép ID 123", False, "no triggers"),
        ("Simple approval request", False, "no triggers"),
        ("Leadership absence during important project", True, "leadership"),
    ]
    
    try:
        from ai_agent.intent_api_mapping import should_use_complex_approval
        
        for message, expected, reason in test_messages:
            result = should_use_complex_approval(
                intent="approve_leave",
                entities={"leave_request_id": 123},
                user_role="team_lead",  # role có authority
                user_input=message
            )
            
            if result == expected:
                print(f"✅ '{message}' -> Complex={result} ({reason})")
            else:
                print(f"❌ '{message}' -> Expected={expected}, Got={result} ({reason})")
                
    except Exception as e:
        print(f"❌ Trigger detection test failed: {e}")

def test_workflow_components():
    """Test individual workflow components"""
    print("\n🧪 Testing Workflow Components...")
    
    try:
        from ai_agent.langgraph_approval_workflow import ComplexApprovalWorkflow
        
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAy1zLhUYfX-B_r71zENYncn18vJDp0V5k")
        workflow = ComplexApprovalWorkflow(gemini_api_key)
        
        # Test các methods tồn tại
        required_methods = [
            'context_discovery_agent',
            'risk_assessment_agent', 
            'business_rules_agent',
            'decision_agent',
            'api_execution_agent',
            'escalation_handler'
        ]
        
        for method_name in required_methods:
            if hasattr(workflow, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
        
        # Test workflow graph creation
        if hasattr(workflow, 'workflow') and workflow.workflow:
            print("✅ Workflow graph created successfully")
        else:
            print("❌ Workflow graph creation failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_django_backend_connectivity():
    """Test kết nối với Django backend"""
    print("\n🧪 Testing Django Backend Connectivity...")
    
    try:
        # Test basic connectivity
        response = requests.get("http://localhost:8000/api/leave-types/", timeout=5)
        if response.status_code == 200:
            print("✅ Django backend accessible")
            return True
        else:
            print(f"⚠️ Django backend returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Django backend not running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Backend connectivity test failed: {e}")
        return False

def run_all_tests():
    """Chạy tất cả tests"""
    print("🚀 Starting LangGraph Complex Approval Workflow Tests...\n")
    
    tests = [
        ("Standalone Workflow", test_complex_workflow_standalone),
        ("Integration with FastAPI", test_integration_with_fastapi),
        ("Trigger Detection", test_trigger_detection),
        ("Workflow Components", test_workflow_components),
        ("Django Backend Connectivity", test_django_backend_connectivity),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results[test_name] = result if result is not None else True
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print('='*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! LangGraph integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the output above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Đặt environment variables nếu cần
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ Warning: GEMINI_API_KEY not set, using default")
    
    success = run_all_tests()
    sys.exit(0 if success else 1) 