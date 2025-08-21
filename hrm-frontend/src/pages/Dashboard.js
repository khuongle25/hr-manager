import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function Dashboard({ user }) {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalDepartments: 0,
    pendingLeaveRequests: 0,
    approvedLeaveRequests: 0,
    myLeaveRequests: 0,
    teamLeaveRequests: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, [user]);

  const fetchStats = async () => {
    try {
      if (user.role === "hr") {
        // HR: Thống kê toàn công ty
        const [usersRes, departmentsRes, leaveRequestsRes] = await Promise.all([
          api.get("/users/"),
          api.get("/departments/"),
          api.get("/leave-requests/"),
        ]);

        const pendingRequests =
          leaveRequestsRes.data.results?.filter(
            (req) => req.status === "pending"
          ) || [];
        const approvedRequests =
          leaveRequestsRes.data.results?.filter(
            (req) => req.status === "approved"
          ) || [];

        setStats({
          totalEmployees: usersRes.data.count || 0,
          totalDepartments: departmentsRes.data.count || 0,
          pendingLeaveRequests: pendingRequests.length,
          approvedLeaveRequests: approvedRequests.length,
          myLeaveRequests: 0,
          teamLeaveRequests: 0,
        });
      } else if (user.role === "team_lead") {
        // Team Lead: Thống kê team
        const [usersRes, leaveRequestsRes] = await Promise.all([
          api.get("/users/"),
          api.get("/leave-requests/"),
        ]);

        const pendingRequests =
          leaveRequestsRes.data.results?.filter(
            (req) => req.status === "pending"
          ) || [];
        const approvedRequests =
          leaveRequestsRes.data.results?.filter(
            (req) => req.status === "approved"
          ) || [];

        setStats({
          totalEmployees: usersRes.data.count || 0,
          totalDepartments: 1, // Chỉ quản lý 1 phòng ban
          pendingLeaveRequests: pendingRequests.length,
          approvedLeaveRequests: approvedRequests.length,
          myLeaveRequests: 0,
          teamLeaveRequests: leaveRequestsRes.data.count || 0,
        });
      } else {
        // Employee: Thống kê cá nhân
        const [leaveRequestsRes, leaveBalanceRes] = await Promise.all([
          api.get("/leave-requests/"),
          api.get("/leave-balances/"),
        ]);

        const myRequests = leaveRequestsRes.data.results || [];
        const pendingRequests = myRequests.filter(
          (req) => req.status === "pending"
        );
        const approvedRequests = myRequests.filter(
          (req) => req.status === "approved"
        );

        setStats({
          totalEmployees: 0,
          totalDepartments: 0,
          pendingLeaveRequests: 0,
          approvedLeaveRequests: 0,
          myLeaveRequests: myRequests.length,
          teamLeaveRequests: 0,
        });
      }
    } catch (error) {
      console.error("Lỗi khi tải thống kê:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleLabel = (role) => {
    const roles = {
      hr: "HR Manager",
      team_lead: "Team Lead",
      employee: "Nhân viên",
    };
    return roles[role] || role;
  };

  if (loading) return <div>Đang tải...</div>;

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ marginBottom: "20px" }}>
        <h1>Dashboard - {getRoleLabel(user?.role)}</h1>
        <p>Chào mừng {user?.full_name}!</p>
      </div>

      {user?.role === "hr" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            marginTop: "20px",
          }}
        >
          <div
            style={{
              background: "#f0f8ff",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Tổng số nhân viên</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#0066cc" }}
            >
              {stats.totalEmployees}
            </p>
          </div>

          <div
            style={{
              background: "#f0fff0",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Tổng số phòng ban</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#006600" }}
            >
              {stats.totalDepartments}
            </p>
          </div>

          <div
            style={{
              background: "#fff8dc",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Đơn nghỉ phép chờ duyệt</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#cc6600" }}
            >
              {stats.pendingLeaveRequests}
            </p>
          </div>

          <div
            style={{
              background: "#f0f0f0",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Đơn nghỉ phép đã duyệt</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#666666" }}
            >
              {stats.approvedLeaveRequests}
            </p>
          </div>
        </div>
      )}

      {user?.role === "team_lead" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            marginTop: "20px",
          }}
        >
          <div
            style={{
              background: "#f0f8ff",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Nhân viên trong team</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#0066cc" }}
            >
              {stats.totalEmployees}
            </p>
          </div>

          <div
            style={{
              background: "#fff8dc",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Đơn nghỉ phép chờ duyệt</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#cc6600" }}
            >
              {stats.pendingLeaveRequests}
            </p>
          </div>

          <div
            style={{
              background: "#f0f0f0",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Đơn nghỉ phép đã duyệt</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#666666" }}
            >
              {stats.approvedLeaveRequests}
            </p>
          </div>

          <div
            style={{
              background: "#e6f3ff",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Tổng đơn nghỉ phép team</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#0066cc" }}
            >
              {stats.teamLeaveRequests}
            </p>
          </div>
        </div>
      )}

      {user?.role === "employee" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            marginTop: "20px",
          }}
        >
          <div
            style={{
              background: "#f0f8ff",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Đơn nghỉ phép của tôi</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#0066cc" }}
            >
              {stats.myLeaveRequests}
            </p>
          </div>

          <div
            style={{
              background: "#f0fff0",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Ngày phép còn lại</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#006600" }}
            >
              Xem chi tiết
            </p>
          </div>

          <div
            style={{
              background: "#fff8dc",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          >
            <h3>Lịch nghỉ phép</h3>
            <p
              style={{ fontSize: "2em", fontWeight: "bold", color: "#cc6600" }}
            >
              Xem lịch
            </p>
          </div>
        </div>
      )}

      <div style={{ marginTop: "30px" }}>
        <h2>Chức năng chính</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "15px",
            marginTop: "15px",
          }}
        >
          {user?.role === "hr" && (
            <>
              <a href="/employees" style={{ textDecoration: "none" }}>
                <button
                  style={{
                    width: "100%",
                    padding: "15px",
                    background: "#007bff",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                  }}
                >
                  Quản lý Nhân viên
                </button>
              </a>
              <a href="/departments" style={{ textDecoration: "none" }}>
                <button
                  style={{
                    width: "100%",
                    padding: "15px",
                    background: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                  }}
                >
                  Quản lý Phòng ban
                </button>
              </a>
            </>
          )}

          {user?.role === "team_lead" && (
            <a href="/employees" style={{ textDecoration: "none" }}>
              <button
                style={{
                  width: "100%",
                  padding: "15px",
                  background: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                Xem Nhân viên Team
              </button>
            </a>
          )}

          <a href="/leave" style={{ textDecoration: "none" }}>
            <button
              style={{
                width: "100%",
                padding: "15px",
                background: "#ffc107",
                color: "black",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
              }}
            >
              {user?.role === "employee"
                ? "Tạo đơn nghỉ phép"
                : "Quản lý Nghỉ phép"}
            </button>
          </a>

          <a href="/profile" style={{ textDecoration: "none" }}>
            <button
              style={{
                width: "100%",
                padding: "15px",
                background: "#17a2b8",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
              }}
            >
              Hồ sơ cá nhân
            </button>
          </a>
        </div>
      </div>
    </div>
  );
}
