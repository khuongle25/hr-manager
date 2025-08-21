import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function EmployeeManagement({ user }) {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "employee",
    department: "",
    phone: "",
    address: "",
    date_of_birth: "",
  });

  useEffect(() => {
    fetchEmployees();
    if (user?.role === "hr") {
      fetchDepartments();
    }
  }, [user]);

  const fetchEmployees = async () => {
    try {
      const response = await api.get("/users/");
      setEmployees(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách nhân viên:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get("/departments/");
      setDepartments(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách phòng ban:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = { ...formData };
      if (submitData.role === "hr") {
        submitData.department_id = "4";
        delete submitData.department;
      } else if (submitData.department) {
        submitData.department_id = submitData.department;
        delete submitData.department;
      }
      if (editingEmployee) {
        // Cập nhật nhân viên
        const updateData = { ...submitData };
        if (!updateData.password) {
          delete updateData.password; // Không gửi password nếu không thay đổi
        }
        delete updateData.username; // Không gửi username khi cập nhật
        await api.patch(`/users/${editingEmployee.id}/`, updateData);
        setEditingEmployee(null);
      } else {
        // Tạo nhân viên mới
        await api.post("/users/", submitData);
      }
      setShowForm(false);
      resetForm();
      fetchEmployees();
    } catch (error) {
      console.error("Lỗi khi lưu nhân viên:", error);
    }
  };

  const handleEdit = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      username: employee.username,
      email: employee.email,
      password: "", // Không hiển thị password cũ
      first_name: employee.first_name || "",
      last_name: employee.last_name || "",
      role: employee.role,
      department: employee.department?.id || "",
      phone: employee.phone || "",
      address: employee.address || "",
      date_of_birth: employee.date_of_birth || "",
    });
    setShowForm(true);
  };

  const handleDelete = async (employeeId) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa nhân viên này?")) {
      try {
        await api.delete(`/users/${employeeId}/`);
        fetchEmployees();
      } catch (error) {
        console.error("Lỗi khi xóa nhân viên:", error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      username: "",
      email: "",
      password: "",
      first_name: "",
      last_name: "",
      role: "employee",
      department: "",
      phone: "",
      address: "",
      date_of_birth: "",
    });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingEmployee(null);
    resetForm();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "role" && value === "hr") {
      setFormData({ ...formData, role: value, department: "4" });
    } else {
      setFormData({ ...formData, [name]: value });
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

  const getPageTitle = () => {
    if (user?.role === "hr") return "Quản lý Nhân viên";
    if (user?.role === "team_lead") return "Nhân viên Team";
    return "Danh sách Nhân viên";
  };

  // Khi chọn role team_lead, trường phòng ban là bắt buộc
  const isTeamLead = formData.role === "team_lead";

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
            {showForm ? "Hủy" : "Thêm nhân viên"}
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
          <h3>{editingEmployee ? "Sửa nhân viên" : "Thêm nhân viên mới"}</h3>
          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "15px",
              }}
            >
              <input
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={editingEmployee} // Không cho sửa username
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <input
                name="email"
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <input
                name="password"
                type="password"
                placeholder={
                  editingEmployee
                    ? "Mật khẩu mới (để trống nếu không đổi)"
                    : "Mật khẩu"
                }
                value={formData.password}
                onChange={handleChange}
                required={!editingEmployee}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <input
                name="first_name"
                placeholder="Họ"
                value={formData.first_name}
                onChange={handleChange}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <input
                name="last_name"
                placeholder="Tên"
                value={formData.last_name}
                onChange={handleChange}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                required
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              >
                <option value="employee">Nhân viên</option>
                <option value="team_lead">Team Lead</option>
                <option value="hr">HR Manager</option>
              </select>
              {formData.role !== "hr" && (
                <select
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  style={{
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #ddd",
                  }}
                  required={isTeamLead}
                >
                  <option value="">Chọn phòng ban</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              )}
              <input
                name="phone"
                placeholder="Số điện thoại"
                value={formData.phone}
                onChange={handleChange}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <input
                name="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={handleChange}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
            </div>
            <textarea
              name="address"
              placeholder="Địa chỉ"
              value={formData.address}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ddd",
                marginTop: "15px",
                minHeight: "80px",
              }}
            />
            <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
              <button
                type="submit"
                style={{
                  padding: "10px 20px",
                  background: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                {editingEmployee ? "Cập nhật" : "Thêm nhân viên"}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                style={{
                  padding: "10px 20px",
                  background: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                Hủy
              </button>
            </div>
          </form>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
          gap: "20px",
        }}
      >
        {employees.map((employee) => (
          <div
            key={employee.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "20px",
              background: "white",
            }}
          >
            <div style={{ marginBottom: "10px" }}>
              <h3 style={{ margin: "0", color: "#333" }}>
                {employee.first_name} {employee.last_name}
              </h3>
              <p style={{ margin: "5px 0", color: "#666" }}>
                @{employee.username}
              </p>
            </div>
            <div style={{ marginBottom: "10px" }}>
              <p style={{ margin: "5px 0" }}>
                <strong>Email:</strong> {employee.email}
              </p>
              <p style={{ margin: "5px 0" }}>
                <strong>Vai trò:</strong> {getRoleLabel(employee.role)}
              </p>
              {employee.department && (
                <p style={{ margin: "5px 0" }}>
                  <strong>Phòng ban:</strong>{" "}
                  {employee.department.id
                    ? `${employee.department.id} - ${employee.department.name}`
                    : employee.department.name || employee.department}
                </p>
              )}
              {employee.phone && (
                <p style={{ margin: "5px 0" }}>
                  <strong>Điện thoại:</strong> {employee.phone}
                </p>
              )}
            </div>
            {user?.role === "hr" && (
              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  onClick={() => handleEdit(employee)}
                  style={{
                    padding: "8px 16px",
                    background: "#ffc107",
                    color: "#333",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Sửa
                </button>
                <button
                  onClick={() => handleDelete(employee.id)}
                  style={{
                    padding: "8px 16px",
                    background: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Xóa
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
