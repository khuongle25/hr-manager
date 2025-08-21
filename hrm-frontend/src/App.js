import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import Profile from "./pages/Profile";
import Dashboard from "./pages/Dashboard";
import EmployeeManagement from "./pages/EmployeeManagement";
import LeaveManagement from "./pages/LeaveManagement";
import LeaveBalanceManagement from "./pages/LeaveBalanceManagement";
import DepartmentManagement from "./pages/DepartmentManagement";
import AIChat from "./pages/AIChat";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access") || "");
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/me/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error("Error fetching user profile:", error);
    }
  };

  const handleLogout = () => {
    setToken("");
    setUser(null);
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  };

  const getRoleLabel = (role) => {
    const roles = {
      hr: "HR Manager",
      team_lead: "Team Lead",
      employee: "Nhân viên",
    };
    return roles[role] || role;
  };

  return (
    <BrowserRouter>
      <nav style={{ background: "#343a40", padding: "15px", color: "white" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            maxWidth: "1200px",
            margin: "0 auto",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <Link
              to="/"
              style={{
                color: "white",
                textDecoration: "none",
                fontWeight: "bold",
              }}
            >
              HR Management
            </Link>
            {token && user && (
              <>
                <Link
                  to="/dashboard"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  Dashboard
                </Link>

                {/* HR Menu */}
                {user.role === "hr" && (
                  <>
                    <Link
                      to="/employees"
                      style={{ color: "white", textDecoration: "none" }}
                    >
                      Quản lý Nhân viên
                    </Link>
                    <Link
                      to="/departments"
                      style={{ color: "white", textDecoration: "none" }}
                    >
                      Quản lý Phòng ban
                    </Link>
                  </>
                )}

                {/* Team Lead Menu */}
                {user.role === "team_lead" && (
                  <Link
                    to="/employees"
                    style={{ color: "white", textDecoration: "none" }}
                  >
                    Nhân viên Team
                  </Link>
                )}

                {/* Common Menu */}
                <Link
                  to="/leave"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  Nghỉ phép
                </Link>
                <Link
                  to="/leave-balance"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  Ngày phép
                </Link>
                <Link
                  to="/profile"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  Hồ sơ
                </Link>
                {/* Thêm mục AI Chatbot */}
                <Link
                  to="/ai-chat"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  AI
                </Link>
              </>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            {!token ? (
              <>
                <Link
                  to="/register"
                  style={{
                    color: "white",
                    textDecoration: "none",
                    marginRight: "15px",
                  }}
                >
                  Đăng ký
                </Link>
                <Link
                  to="/login"
                  style={{ color: "white", textDecoration: "none" }}
                >
                  Đăng nhập
                </Link>
              </>
            ) : (
              <>
                {user && (
                  <span style={{ fontSize: "14px" }}>
                    {user.full_name} ({getRoleLabel(user.role)})
                  </span>
                )}
                <Link
                  to="/logout"
                  style={{
                    background: "#dc3545",
                    color: "white",
                    border: "none",
                    padding: "8px 16px",
                    borderRadius: "4px",
                    cursor: "pointer",
                    textDecoration: "none",
                    display: "inline-block",
                  }}
                >
                  Đăng xuất
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px" }}>
        <Routes>
          <Route
            path="/"
            element={
              token ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/dashboard"
            element={
              token ? <Dashboard user={user} /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/employees"
            element={
              token ? (
                <EmployeeManagement user={user} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/departments"
            element={
              token ? (
                <DepartmentManagement user={user} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/leave"
            element={
              token ? <LeaveManagement user={user} /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/leave-balance"
            element={
              token ? (
                <LeaveBalanceManagement user={user} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/profile"
            element={token ? <Profile user={user} /> : <Navigate to="/login" />}
          />
          <Route
            path="/logout"
            element={
              token ? (
                <Logout handleLogout={handleLogout} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/login"
            element={
              !token ? (
                <Login setToken={setToken} setUser={setUser} />
              ) : (
                <Navigate to="/dashboard" />
              )
            }
          />
          <Route path="/register" element={<Navigate to="/login" />} />
          <Route path="/ai-chat" element={<AIChat />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
