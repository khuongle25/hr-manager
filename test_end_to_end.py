#!/usr/bin/env python3
"""
End-to-End Test cho LangGraph Complex Approval
Test thực tế với FastAPI + Django backends
"""

import requests
import json
import time

def test_simple_vs_complex_approval():
    """Test sự khác biệt giữa simple và complex approval"""
    
    print("🧪 End-to-End Test: Simple vs Complex Approval Workflow")
    print("="*70)
    
    # FastAPI endpoint  
    ai_api_url = "http://localhost:9000/chat"
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Approval (Should use simple logic)",
            "payload": {
                "user_id": 1,
                "role": "team_lead",
                "message": "Duyệt đơn nghỉ phép ID 20",
                "token": "mock_token_test"
            },
            "expected_workflow": "simple"
        },
        {
            "name": "Complex Approval (Should use LangGraph)",
            "payload": {
                "user_id": 28,
                "role": "hr", 
                "message": "Duyệt đơn nghỉ phép ID 21 team lead cuối năm có conflict với team members critical deadline",
                "token": "mock_token_test"
            },
            "expected_workflow": "langgraph_complex"
        },
        {
            "name": "Complex with Overlap Keywords",
            "payload": {
                "user_id": 28,
                "role": "hr",
                "message": "Duyệt đơn ID 21 overlap department leadership absence",
                "token": "mock_token_test"
            },
            "expected_workflow": "langgraph_complex"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Gửi request tới FastAPI
            print(f"📤 Sending request: {test_case['payload']['message']}")
            
            response = requests.post(ai_api_url, json=test_case["payload"], timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Response received")
                print(f"📊 User Message: {result.get('user_message', '')[:200]}...")
                print(f"🎯 Intent: {result.get('intent', 'N/A')}")
                print(f"📋 Entities: {result.get('entities', {})}")
                
                # Check workflow used
                if "workflow_used" in result:
                    workflow_used = result["workflow_used"]
                    expected = test_case["expected_workflow"]
                    
                    if workflow_used == expected:
                        print(f"✅ Correct workflow used: {workflow_used}")
                    else:
                        print(f"❌ Wrong workflow: Expected {expected}, Got {workflow_used}")
                    
                    # Show LangGraph specific results
                    if workflow_used == "langgraph_complex":
                        risk_assessment = result.get("risk_assessment", {})
                        print(f"🎯 Risk Score: {risk_assessment.get('risk_score', 0)}/100")
                        print(f"⚠️ Conflicts: {len(risk_assessment.get('conflicts', []))}")
                        print(f"🚨 Risks: {len(risk_assessment.get('risks', []))}")
                        print(f"📋 Business Rules: {risk_assessment.get('business_rules', [])}")
                        
                        # Print detailed risk info if available
                        for conflict in risk_assessment.get('conflicts', [])[:2]:  # Show first 2
                            print(f"   ⚠️ {conflict.get('type')}: {conflict.get('details', '')}")
                        
                        for risk in risk_assessment.get('risks', [])[:2]:  # Show first 2
                            print(f"   🚨 {risk.get('type')}: {risk.get('details', '')}")
                
                else:
                    # Simple workflow - check if it avoided complex processing
                    if test_case["expected_workflow"] == "simple":
                        print(f"✅ Used simple workflow (no complex processing)")
                    else:
                        print(f"⚠️ Expected complex workflow but used simple")
                        
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ FastAPI server not running on localhost:9000")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print()  # Empty line between tests

def test_mock_complex_workflow():
    """Test complex workflow với mock data"""
    print("\n🧪 Mock Complex Workflow Test")
    print("="*70)
    
    # Test với logic mock để show workflow steps
    ai_api_url = "http://localhost:9000/chat"
    
    complex_scenario = {
        "user_id": 28,
        "role": "hr",
        "message": "Cần duyệt gấp đơn nghỉ phép ID 21 của team lead trong thời gian critical project deadline cuối năm, có overlap với 3 team members khác đã nghỉ",
        "token": "mock_complex_test"
    }
    
    print(f"📤 Complex Scenario: {complex_scenario['message']}")
    print()
    
    try:
        response = requests.post(ai_api_url, json=complex_scenario, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Complex Processing Complete!")
            print(f"🎯 Intent: {result.get('intent')}")
            print(f"📋 Entities: {result.get('entities')}")
            
            if result.get("workflow_used") == "langgraph_complex":
                print(f"\n🤖 LangGraph Complex Workflow Results:")
                print("-" * 40)
                
                risk_assessment = result.get("risk_assessment", {})
                print(f"📊 Risk Score: {risk_assessment.get('risk_score', 0)}/100")
                
                conflicts = risk_assessment.get('conflicts', [])
                risks = risk_assessment.get('risks', [])
                business_rules = risk_assessment.get('business_rules', [])
                
                print(f"\n⚠️ Conflicts Detected ({len(conflicts)}):")
                for conflict in conflicts:
                    print(f"   • {conflict.get('type', 'Unknown')}: {conflict.get('details', '')}")
                
                print(f"\n🚨 Risks Identified ({len(risks)}):")
                for risk in risks:
                    print(f"   • {risk.get('type', 'Unknown')}: {risk.get('details', '')}")
                
                print(f"\n📋 Business Rules Triggered ({len(business_rules)}):")
                for rule in business_rules:
                    print(f"   • {rule}")
                
                # Show escalation info
                execution_result = result.get("result", {})
                if execution_result.get("escalated"):
                    print(f"\n🆘 ESCALATED: {execution_result.get('escalation_reason', '')}")
                    print(f"🎫 Ticket ID: {execution_result.get('escalation_ticket_id', '')}")
                
            print(f"\n💬 Final Response:")
            print(f"{result.get('user_message', '')}")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Mock test failed: {e}")

def check_services():
    """Kiểm tra các services đang chạy"""
    print("🔍 Checking Services...")
    print("="*30)
    
    services = [
        ("FastAPI AI Backend", "http://localhost:9000/", "GET"),
        ("Django Backend", "http://localhost:8000/api/", "GET"),
    ]
    
    for name, url, method in services:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
                
            if response.status_code < 500:
                print(f"✅ {name}: Running (HTTP {response.status_code})")
            else:
                print(f"⚠️ {name}: Issues (HTTP {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Not running")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

if __name__ == "__main__":
    print("🚀 LangGraph Complex Approval - End-to-End Testing")
    print("="*70)
    
    # Check services first
    check_services()
    
    print("\n" + "="*70)
    
    # Test simple vs complex routing
    test_simple_vs_complex_approval()
    
    # Test complex workflow with detailed mock
    test_mock_complex_workflow()
    
    print("\n🎉 End-to-End Testing Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Simple vs Complex workflow routing")
    print("   ✅ LangGraph multi-agent processing")
    print("   ✅ Risk assessment & conflict detection")
    print("   ✅ Business rules application")
    print("   ✅ Escalation handling")
    print("   ✅ Intelligent decision making") 