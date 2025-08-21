import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function LeaveBalanceManagement({ user }) {
  const [leaveBalances, setLeaveBalances] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    employee: "",
    leave_type: "",
    balance: "",
  });

  useEffect(() => {
    fetchLeaveBalances();
    if (user?.role === "hr") {
      fetchLeaveTypes();
      fetchEmployees();
    }
  }, [user]);

  const fetchLeaveBalances = async () => {
    try {
      const response = await api.get("/leave-balances/");
      setLeaveBalances(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách ngày phép:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaveTypes = async () => {
    try {
      const response = await api.get("/leave-types/");
      setLeaveTypes(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách loại nghỉ phép:", error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await api.get("/users/");
      setEmployees(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách nhân viên:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        leave_type_id: formData.leave_type,
      };
      delete submitData.leave_type;

      const response = await api.post("/leave-balances/", submitData);

      if (response.status === 200) {
        alert("Đã cập nhật ngày phép thành công!");
      } else {
        alert("Đã tạo ngày phép mới thành công!");
      }

      setShowForm(false);
      setFormData({
        employee: "",
        leave_type: "",
        balance: "",
      });
      fetchLeaveBalances();
    } catch (error) {
      console.error("Lỗi khi tạo ngày phép:", error);
      if (error.response?.data?.detail) {
        alert(`Lỗi: ${error.response.data.detail}`);
      } else {
        alert("Có lỗi xảy ra khi tạo ngày phép!");
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const getPageTitle = () => {
    if (user?.role === "hr") return "Quản lý Ngày phép (Toàn công ty)";
    if (user?.role === "team_lead") return "Ngày phép Team";
    return "Ngày phép của tôi";
  };

  const getStatusColor = (balance, used) => {
    const remaining = balance - used;
    if (remaining <= 0) return "#dc3545"; // Đỏ
    if (remaining <= 3) return "#ffc107"; // Vàng
    return "#28a745"; // Xanh
  };

  if (loading) return <div>Đang tải...</div>;

  return (
    <div style={{ padding: "20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h1>{getPageTitle()}</h1>
        {user?.role === "hr" && (
          <button
            onClick={() => setShowForm(!showForm)}
            style={{
              padding: "10px 20px",
              background: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            {showForm ? "Hủy" : "Thêm ngày phép"}
          </button>
        )}
      </div>

      {user?.role === "hr" && showForm && (
        <div
          style={{
            background: "#f8f9fa",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "20px",
          }}
        >
          <h3>Thêm ngày phép mới</h3>
          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "15px",
              }}
            >
              <select
                name="employee"
                value={formData.employee}
                onChange={handleChange}
                required
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              >
                <option value="">Chọn nhân viên</option>
                {employees.map((employee) => (
                  <option key={employee.id} value={employee.id}>
                    {employee.full_name} ({employee.username})
                  </option>
                ))}
              </select>
              <select
                name="leave_type"
                value={formData.leave_type}
                onChange={handleChange}
                required
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              >
                <option value="">Chọn loại nghỉ phép</option>
                {leaveTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
              <input
                name="balance"
                type="number"
                placeholder="Số ngày phép"
                value={formData.balance}
                onChange={handleChange}
                required
                min="0"
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
            </div>
            <button
              type="submit"
              style={{
                marginTop: "15px",
                padding: "10px 20px",
                background: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
              }}
            >
              Thêm ngày phép
            </button>
          </form>
        </div>
      )}

      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "white",
          }}
        >
          <thead>
            <tr style={{ background: "#f8f9fa" }}>
              {user?.role !== "employee" && (
                <th
                  style={{
                    padding: "12px",
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                  }}
                >
                  Nhân viên
                </th>
              )}
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Loại nghỉ phép
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Tổng ngày phép
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Đã sử dụng
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Còn lại
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Trạng thái
              </th>
            </tr>
          </thead>
          <tbody>
            {leaveBalances.map((balance) => {
              const remaining =
                balance.remaining || balance.balance - (balance.used || 0);
              const used = balance.used || 0;
              const statusColor = getStatusColor(balance.balance, used);
              const statusText =
                remaining <= 0
                  ? "Hết phép"
                  : remaining <= 3
                  ? "Sắp hết"
                  : "Còn nhiều";

              return (
                <tr key={balance.id} style={{ borderBottom: "1px solid #eee" }}>
                  {user?.role !== "employee" && (
                    <td style={{ padding: "12px" }}>
                      {balance.employee?.full_name}
                    </td>
                  )}
                  <td style={{ padding: "12px" }}>
                    {balance.leave_type?.name}
                  </td>
                  <td style={{ padding: "12px" }}>
                    <strong>{balance.balance}</strong> ngày
                  </td>
                  <td style={{ padding: "12px" }}>{used} ngày</td>
                  <td style={{ padding: "12px" }}>
                    <strong style={{ color: statusColor }}>
                      {remaining} ngày
                    </strong>
                  </td>
                  <td style={{ padding: "12px" }}>
                    <span
                      style={{
                        padding: "4px 8px",
                        borderRadius: "4px",
                        background: statusColor,
                        color: "white",
                        fontSize: "12px",
                      }}
                    >
                      {statusText}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {leaveBalances.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#6c757d" }}>
          <p>Chưa có thông tin ngày phép nào.</p>
        </div>
      )}
    </div>
  );
}
