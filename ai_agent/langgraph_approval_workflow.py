"""
LangGraph Complex Approval Workflow
Xử lý các trường hợp duyệt đơn phức tạp có conflict, risk assessment
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import operator
import requests
import json
from datetime import datetime, date, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# ================================
# STATE DEFINITION
# ================================

class ComplexApprovalState(TypedDict):
    """State cho complex approval workflow"""
    # Input từ user
    user_input: str
    user_id: int
    user_role: str
    user_token: str
    intent: str
    entities: Dict[str, Any]
    
    # Discovered context
    leave_request: Optional[Dict]
    employee_context: Optional[Dict]
    team_context: Optional[Dict]
    department_context: Optional[Dict]
    
    # Risk assessment 
    conflicts: Annotated[List[Dict], operator.add]
    risks: Annotated[List[Dict], operator.add]
    business_rules_triggered: Annotated[List[str], operator.add]
    
    # Processing results
    risk_score: int  # 0-100
    requires_escalation: bool
    escalation_reason: str
    recommended_action: str  # "approve", "deny", "escalate", "request_info"
    
    # Final output
    api_calls: Annotated[List[Dict], operator.add]
    user_message: str
    execution_result: Dict[str, Any]

# ================================
# LANGGRAPH WORKFLOW
# ================================

class ComplexApprovalWorkflow:
    def __init__(self, gemini_api_key: str, api_base: str = "http://localhost:8000/api"):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=gemini_api_key
        )
        self.api_base = api_base
        
        # Tạo workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Tạo LangGraph workflow"""
        workflow = StateGraph(ComplexApprovalState)
        
        # Thêm các nodes
        workflow.add_node("context_discovery", self.context_discovery_agent)
        workflow.add_node("risk_assessment", self.risk_assessment_agent)
        workflow.add_node("business_rules", self.business_rules_agent)
        workflow.add_node("decision_agent", self.decision_agent)
        workflow.add_node("api_execution", self.api_execution_agent)
        workflow.add_node("escalation_handler", self.escalation_handler)
        
        # Set entry point
        workflow.set_entry_point("context_discovery")
        
        # Thêm edges - conditional routing
        workflow.add_edge("context_discovery", "risk_assessment")
        workflow.add_edge("risk_assessment", "business_rules")
        workflow.add_conditional_edges(
            "business_rules",
            self._should_escalate,
            {
                "escalate": "escalation_handler",
                "continue": "decision_agent"
            }
        )
        workflow.add_conditional_edges(
            "decision_agent", 
            self._decision_routing,
            {
                "execute": "api_execution",
                "escalate": "escalation_handler",
                "end": END
            }
        )
        workflow.add_edge("api_execution", END)
        workflow.add_edge("escalation_handler", END)
        
        return workflow.compile()
    
    def _should_escalate(self, state: ComplexApprovalState) -> str:
        """Conditional edge function - có cần escalate không"""
        if state["risk_score"] > 75 or state["requires_escalation"]:
            return "escalate"
        return "continue"
    
    def _decision_routing(self, state: ComplexApprovalState) -> str:
        """Conditional edge function - routing decision"""
        action = state["recommended_action"]
        if action == "escalate":
            return "escalate"
        elif action in ["approve", "deny"]:
            return "execute"
        else:
            return "end"
    
    # ================================
    # AGENT NODES
    # ================================
    
    def context_discovery_agent(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 1: Thu thập context đầy đủ"""
        print("🔍 Context Discovery Agent: Gathering comprehensive context...")
        
        headers = {"Authorization": f"Bearer {state['user_token']}"}
        leave_request_id = state["entities"].get("leave_request_id")
        
        if not leave_request_id:
            state["user_message"] = "❌ Không tìm thấy ID đơn nghỉ phép để xử lý"
            return state
        
        try:
            # 1. Lấy chi tiết leave request
            leave_resp = requests.get(f"{self.api_base}/leave-requests/{leave_request_id}/", 
                                      headers=headers, timeout=10)
            if leave_resp.status_code == 200:
                state["leave_request"] = leave_resp.json()
                print(f"✅ Retrieved leave request: {leave_request_id}")
            else:
                state["user_message"] = f"❌ Không thể lấy thông tin đơn nghỉ phép ID {leave_request_id}"
                return state
            
            # 2. Lấy thông tin employee
            employee = state["leave_request"]["employee"]
            if isinstance(employee, dict):
                employee_id = employee.get("id")
                state["employee_context"] = employee
                print(f"✅ Retrieved employee context: {employee.get('full_name')}")
            
            # 3. Lấy thông tin department
            department = state["leave_request"]["department"]
            if isinstance(department, dict):
                dept_id = department.get("id")
                dept_resp = requests.get(f"{self.api_base}/departments/{dept_id}/", 
                                         headers=headers, timeout=5)
                if dept_resp.status_code == 200:
                    state["department_context"] = dept_resp.json()
                    print(f"✅ Retrieved department context: {department.get('name')}")
            
            # 4. Lấy thông tin team (all department members)
            if state["department_context"]:
                team_members = state["department_context"].get("members", [])
                state["team_context"] = {"members": team_members, "size": len(team_members)}
                print(f"✅ Retrieved team context: {len(team_members)} members")
            
        except Exception as e:
            print(f"❌ Context discovery error: {e}")
            state["user_message"] = f"❌ Lỗi khi thu thập thông tin: {str(e)}"
        
        return state
    
    def risk_assessment_agent(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 2: Đánh giá risk và conflicts"""
        print("⚠️ Risk Assessment Agent: Analyzing risks and conflicts...")
        
        if not state.get("leave_request"):
            return state
        
        leave = state["leave_request"]
        employee = state["employee_context"]
        team = state["team_context"]
        
        # Khởi tạo risk score
        risk_score = 0
        conflicts = []
        risks = []
        
        try:
            # 1. CONFLICT: Kiểm tra team overlap - có ai khác cũng nghỉ cùng thời gian?
            start_date = datetime.strptime(leave["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(leave["end_date"], "%Y-%m-%d").date()
            
            # Lấy tất cả leave requests trong thời gian này
            headers = {"Authorization": f"Bearer {state['user_token']}"}
            leaves_resp = requests.get(f"{self.api_base}/leave-requests/", 
                                      params={"start_date": leave["start_date"], 
                                             "end_date": leave["end_date"]},
                                      headers=headers, timeout=10)
            
            if leaves_resp.status_code == 200:
                overlapping_leaves = leaves_resp.json()
                if isinstance(overlapping_leaves, dict) and "results" in overlapping_leaves:
                    overlapping_leaves = overlapping_leaves["results"]
                
                # Filter: chỉ những đơn approved và cùng department
                approved_overlaps = []
                for other_leave in overlapping_leaves:
                    if (other_leave.get("status") == "approved" and 
                        other_leave.get("id") != leave["id"] and
                        other_leave.get("department", {}).get("id") == leave.get("department", {}).get("id")):
                        approved_overlaps.append(other_leave)
                
                if approved_overlaps:
                    conflict = {
                        "type": "TEAM_OVERLAP",
                        "severity": "HIGH" if len(approved_overlaps) >= 2 else "MEDIUM",
                        "details": f"{len(approved_overlaps)} members cùng team đã nghỉ trong thời gian này",
                        "affected_employees": [ol.get("employee", {}).get("full_name") for ol in approved_overlaps]
                    }
                    conflicts.append(conflict)
                    risk_score += 30 if len(approved_overlaps) >= 2 else 15
                    print(f"⚠️ Team overlap conflict detected: {len(approved_overlaps)} overlaps")
            
            # 2. RISK: Kiểm tra critical period (cuối năm, deadline)
            current_date = date.today()
            if start_date.month == 12 and start_date.day > 15:
                risk = {
                    "type": "CRITICAL_PERIOD",
                    "severity": "HIGH",
                    "details": "Nghỉ phép trong period cuối năm (sau 15/12)"
                }
                risks.append(risk)
                risk_score += 25
                print("⚠️ Critical period risk: End of year leave")
            
            # 3. RISK: Team Lead nghỉ phép
            if employee and employee.get("role") == "team_lead":
                risk = {
                    "type": "LEADERSHIP_ABSENCE", 
                    "severity": "HIGH",
                    "details": "Team Lead nghỉ phép - cần coverage plan"
                }
                risks.append(risk)
                risk_score += 20
                print("⚠️ Leadership absence risk detected")
            
            # 4. RISK: Nghỉ phép dài (> 5 ngày)
            duration = (end_date - start_date).days + 1
            if duration > 5:
                risk = {
                    "type": "EXTENDED_LEAVE",
                    "severity": "MEDIUM",
                    "details": f"Nghỉ phép kéo dài {duration} ngày"
                }
                risks.append(risk)
                risk_score += 10
                print(f"⚠️ Extended leave risk: {duration} days")
            
            # 5. RISK: Short notice (< 3 ngày)
            created_date = datetime.strptime(leave["created_at"][:10], "%Y-%m-%d").date()
            notice_days = (start_date - created_date).days
            if notice_days < 3:
                risk = {
                    "type": "SHORT_NOTICE",
                    "severity": "MEDIUM", 
                    "details": f"Báo trước chỉ {notice_days} ngày"
                }
                risks.append(risk)
                risk_score += 15
                print(f"⚠️ Short notice risk: {notice_days} days")
                
        except Exception as e:
            print(f"❌ Risk assessment error: {e}")
            # Không return lỗi, cứ tiếp tục với risk score hiện tại
        
        # Cập nhật state
        state["conflicts"] = conflicts
        state["risks"] = risks  
        state["risk_score"] = min(risk_score, 100)  # Cap at 100
        
        print(f"📊 Risk Assessment Complete: Score {state['risk_score']}, {len(conflicts)} conflicts, {len(risks)} risks")
        
        return state
    
    def business_rules_agent(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 3: Áp dụng business rules"""
        print("📋 Business Rules Agent: Applying company policies...")
        
        rules_triggered = []
        requires_escalation = False
        escalation_reason = ""
        
        # Rule 1: High risk score requires escalation
        if state["risk_score"] > 70:
            rules_triggered.append("HIGH_RISK_ESCALATION")
            requires_escalation = True
            escalation_reason = f"Risk score cao ({state['risk_score']}/100) - cần review từ cấp cao hơn"
        
        # Rule 2: Team Lead + Team overlap = CEO approval required
        employee = state.get("employee_context", {})
        if (employee.get("role") == "team_lead" and 
            any(c["type"] == "TEAM_OVERLAP" for c in state.get("conflicts", []))):
            rules_triggered.append("TEAM_LEAD_OVERLAP_CEO_APPROVAL")
            requires_escalation = True
            escalation_reason = "Team Lead nghỉ phép + team overlap - cần CEO approval"
        
        # Rule 3: Critical period + >3 people = Block
        critical_period = any(r["type"] == "CRITICAL_PERIOD" for r in state.get("risks", []))
        team_overlap_high = any(c["type"] == "TEAM_OVERLAP" and c["severity"] == "HIGH" 
                               for c in state.get("conflicts", []))
        if critical_period and team_overlap_high:
            rules_triggered.append("CRITICAL_PERIOD_BLOCK")
            requires_escalation = True
            escalation_reason = "Thời gian critical + nhiều người nghỉ - recommend block"
        
        # Rule 4: Consecutive Team Lead leaves (advanced rule)
        if employee.get("role") == "team_lead":
            rules_triggered.append("TEAM_LEAD_SUCCESSION_PLAN")
            if not escalation_reason:
                escalation_reason = "Team Lead leave - cần xác nhận succession plan"
        
        state["business_rules_triggered"] = rules_triggered
        state["requires_escalation"] = requires_escalation
        state["escalation_reason"] = escalation_reason
        
        print(f"📋 Business Rules: {len(rules_triggered)} rules triggered, Escalation: {requires_escalation}")
        
        return state
    
    def decision_agent(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 4: Quyết định cuối cùng sử dụng AI"""
        print("🤖 Decision Agent: Making intelligent decision...")
        
        # Chuẩn bị context cho AI decision
        context = {
            "leave_request": state.get("leave_request"),
            "employee": state.get("employee_context"),
            "risk_score": state.get("risk_score", 0),
            "conflicts": state.get("conflicts", []),
            "risks": state.get("risks", []),
            "business_rules": state.get("business_rules_triggered", []),
            "user_role": state["user_role"]
        }
        
        # AI Prompt cho decision making
        prompt = f"""
        Bạn là AI Decision Agent cho hệ thống HR. Hãy phân tích context và đưa ra quyết định:

        CONTEXT:
        - User Role: {state['user_role']}
        - Employee: {context['employee'].get('full_name')} ({context['employee'].get('role')})
        - Leave Period: {context['leave_request'].get('start_date')} to {context['leave_request'].get('end_date')}
        - Risk Score: {context['risk_score']}/100
        - Conflicts: {len(context['conflicts'])} detected
        - Risks: {len(context['risks'])} identified
        - Business Rules Triggered: {context['business_rules']}

        DETAILED ANALYSIS:
        Conflicts: {json.dumps(context['conflicts'], indent=2)}
        Risks: {json.dumps(context['risks'], indent=2)}

        Hãy quyết định một trong các action:
        - "approve": Duyệt đơn (risk thấp, không có conflict nghiêm trọng)
        - "deny": Từ chối (risk cao, conflict nghiêm trọng)
        - "escalate": Chuyển lên cấp cao hơn (cần human judgment)
        - "request_info": Cần thêm thông tin

        Trả về JSON format:
        {{
            "action": "<action>",
            "reasoning": "<lý do chi tiết>",
            "conditions": ["<điều kiện nếu approve>"],
            "alternative_dates": "<gợi ý ngày khác nếu có conflict>"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            decision_text = response.content.strip()
            
            # Parse JSON response
            if decision_text.startswith("```"):
                decision_text = decision_text.split("```")[1]
                if decision_text.startswith("json"):
                    decision_text = decision_text[4:]
            
            decision = json.loads(decision_text)
            
            state["recommended_action"] = decision.get("action", "escalate")
            state["user_message"] = decision.get("reasoning", "AI decision completed")
            
            print(f"🤖 AI Decision: {state['recommended_action']} - {decision.get('reasoning', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ AI Decision error: {e}")
            # Fallback decision based on risk score
            if state["risk_score"] > 75:
                state["recommended_action"] = "escalate"
                state["user_message"] = "Risk score cao - chuyển escalation"
            elif state["risk_score"] > 50:
                state["recommended_action"] = "request_info"
                state["user_message"] = "Cần thêm thông tin trước khi quyết định"
            else:
                state["recommended_action"] = "approve"
                state["user_message"] = "Risk thấp - recommend approve"
        
        return state
    
    def api_execution_agent(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 5: Thực thi API calls"""
        print("🚀 API Execution Agent: Executing decision...")
        
        action = state["recommended_action"]
        leave_request_id = state["entities"].get("leave_request_id")
        headers = {"Authorization": f"Bearer {state['user_token']}"}
        
        try:
            if action == "approve":
                resp = requests.post(f"{self.api_base}/leave-requests/{leave_request_id}/approve/", 
                                   headers=headers, timeout=10)
                if resp.status_code < 400:
                    result = resp.json()
                    state["execution_result"] = result
                    state["user_message"] = f"✅ Đã duyệt đơn ID {leave_request_id} thành công!\n\n{state['user_message']}"
                else:
                    error = resp.json() if resp.content else {"detail": "Unknown error"}
                    state["execution_result"] = {"error": error}
                    state["user_message"] = f"❌ Lỗi khi duyệt đơn: {error.get('detail', 'Unknown error')}"
                    
            elif action == "deny":
                resp = requests.post(f"{self.api_base}/leave-requests/{leave_request_id}/deny/", 
                                   headers=headers, timeout=10)
                if resp.status_code < 400:
                    result = resp.json()
                    state["execution_result"] = result
                    state["user_message"] = f"❌ Đã từ chối đơn ID {leave_request_id}.\n\n{state['user_message']}"
                else:
                    error = resp.json() if resp.content else {"detail": "Unknown error"}
                    state["execution_result"] = {"error": error}
                    state["user_message"] = f"❌ Lỗi khi từ chối đơn: {error.get('detail', 'Unknown error')}"
            
        except Exception as e:
            print(f"❌ API Execution error: {e}")
            state["execution_result"] = {"error": str(e)}
            state["user_message"] = f"❌ Lỗi khi thực thi: {str(e)}"
        
        return state
    
    def escalation_handler(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Agent 6: Xử lý escalation cases"""
        print("🆘 Escalation Handler: Creating escalation ticket...")
        
        # Tạo escalation summary
        employee = state.get("employee_context", {})
        leave = state.get("leave_request", {})
        
        escalation_summary = f"""
🆘 ESCALATION REQUIRED - Leave Request ID {leave.get('id')}

👤 EMPLOYEE: {employee.get('full_name')} ({employee.get('role')})
📅 PERIOD: {leave.get('start_date')} to {leave.get('end_date')}
📊 RISK SCORE: {state.get('risk_score', 0)}/100

⚠️ REASON: {state.get('escalation_reason', 'High complexity detected')}

🔍 CONFLICTS DETECTED:
{json.dumps(state.get('conflicts', []), indent=2)}

⚠️ RISKS IDENTIFIED:
{json.dumps(state.get('risks', []), indent=2)}

📋 BUSINESS RULES TRIGGERED:
{state.get('business_rules_triggered', [])}

💡 RECOMMENDED ACTIONS:
- Review team coverage plan
- Consider alternative dates
- Assess business impact
- Coordinate with department head

🔗 REVIEW URL: /leave-requests/{leave.get('id')}/
        """
        
        state["user_message"] = escalation_summary
        state["execution_result"] = {
            "escalated": True,
            "escalation_ticket_id": f"ESC-{leave.get('id')}-{datetime.now().strftime('%Y%m%d%H%M')}",
            "escalation_reason": state.get("escalation_reason"),
            "risk_assessment": {
                "risk_score": state.get("risk_score"),
                "conflicts": state.get("conflicts", []),
                "risks": state.get("risks", [])
            }
        }
        
        print("🆘 Escalation ticket created successfully")
        
        return state
    
    # ================================
    # PUBLIC METHODS
    # ================================
    
    def should_use_complex_workflow(self, intent: str, entities: Dict, user_role: str) -> bool:
        """Quyết định có nên dùng complex workflow không"""
        
        # Chỉ dùng cho approve/deny
        if intent not in ["approve_leave", "deny_leave"]:
            return False
        
        # Nếu user là HR thì có thể handle case phức tạp bằng workflow
        # Nếu user là team_lead thì cũng có thể cần complex analysis
        if user_role in ["hr", "team_lead"]:
            # Có thể thêm logic check thêm ở đây
            # Ví dụ: có mention về "team lead", "end of year", "overlap" trong user message
            return True
        
        return False
    
    def execute(self, state: ComplexApprovalState) -> ComplexApprovalState:
        """Thực thi workflow"""
        print("🎯 Starting Complex Approval Workflow...")
        
        try:
            # Run the workflow
            result = self.workflow.invoke(state)
            print("✅ Complex Approval Workflow completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            return {
                **state,
                "user_message": f"❌ Lỗi trong quá trình xử lý phức tạp: {str(e)}",
                "execution_result": {"error": str(e)}
            }

# ================================
# INTEGRATION FUNCTION
# ================================

def create_complex_approval_workflow(gemini_api_key: str) -> ComplexApprovalWorkflow:
    """Factory function để tạo workflow instance"""
    return ComplexApprovalWorkflow(gemini_api_key) 