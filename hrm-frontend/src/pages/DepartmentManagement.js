import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function DepartmentManagement() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    lead_email: "",
  });
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    fetchDepartments();
    fetchEmployees();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await api.get("/departments/");
      setDepartments(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách phòng ban:", error);
    } finally {
      setLoading(false);
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
      const submitData = { ...formData };
      if (editingId) {
        await api.put(`/departments/${editingId}/`, submitData);
      } else {
        await api.post("/departments/", submitData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({
        name: "",
        description: "",
        lead_email: "",
      });
      fetchDepartments();
    } catch (error) {
      console.error("Lỗi khi lưu phòng ban:", error);
    }
  };

  const handleEdit = (department) => {
    setEditingId(department.id);
    setFormData({
      name: department.name,
      description: department.description || "",
      lead_email:
        department.lead && department.lead.length > 0
          ? department.lead[0].email
          : "",
    });
    setShowForm(true);
  };

  const handleDelete = async (departmentId) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa phòng ban này?")) {
      try {
        await api.delete(`/departments/${departmentId}/`);
        fetchDepartments();
      } catch (error) {
        console.error("Lỗi khi xóa phòng ban:", error);
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({
      name: "",
      description: "",
      lead_email: "",
    });
  };

  const assignLead = async (departmentId) => {
    const email = prompt(
      "Nhập email của Tech Lead muốn bổ nhiệm làm lead phòng ban:"
    );
    if (!email) return;
    try {
      await api.post(`/departments/${departmentId}/assign-lead/`, { email });
      alert("Bổ nhiệm thành công!");
      fetchDepartments();
    } catch (err) {
      alert(
        "Bổ nhiệm thất bại: " +
          (err.response?.data?.error || "Lỗi không xác định")
      );
    }
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
        <h1>Quản lý Phòng ban</h1>
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
          {showForm ? "Hủy" : "Thêm phòng ban"}
        </button>
      </div>

      {showForm && (
        <div
          style={{
            background: "#f8f9fa",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "20px",
          }}
        >
          <h3>{editingId ? "Sửa phòng ban" : "Thêm phòng ban mới"}</h3>
          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "15px",
              }}
            >
              <input
                name="name"
                placeholder="Tên phòng ban"
                value={formData.name}
                onChange={handleChange}
                required
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
              />
              <select
                name="lead_email"
                value={formData.lead_email}
                onChange={handleChange}
                style={{
                  padding: "8px",
                  borderRadius: "4px",
                  border: "1px solid #ddd",
                }}
                required
              >
                <option value="">Chọn Team Lead</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.email}>
                    {emp.first_name} {emp.last_name} ({emp.email})
                  </option>
                ))}
              </select>
            </div>
            <textarea
              name="description"
              placeholder="Mô tả phòng ban"
              value={formData.description}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "8px",
                borderRadius: "4px",
                border: "1px solid #ddd",
                marginTop: "10px",
              }}
              rows="3"
            />
            <div style={{ marginTop: "10px" }}>
              <button
                type="submit"
                style={{
                  marginRight: "10px",
                  padding: "10px 20px",
                  background: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                {editingId ? "Cập nhật" : "Tạo phòng ban"}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                style={{
                  padding: "10px 20px",
                  background: "#dc3545",
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
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                ID
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Tên phòng ban
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Mô tả
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Quản lý
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Số nhân viên
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Ngày tạo
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Thao tác
              </th>
            </tr>
          </thead>
          <tbody>
            {departments.map((department) => (
              <tr
                key={department.id}
                style={{ borderBottom: "1px solid #eee" }}
              >
                <td style={{ padding: "12px" }}>{department.id}</td>
                <td style={{ padding: "12px", fontWeight: "bold" }}>
                  {department.name}
                </td>
                <td style={{ padding: "12px", maxWidth: "200px" }}>
                  <div
                    style={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {department.description || "-"}
                  </div>
                </td>
                <td style={{ padding: "12px" }}>
                  {department.lead && department.lead.length > 0
                    ? department.lead.map((l) => l.full_name).join(", ")
                    : "-"}
                </td>
                <td style={{ padding: "12px" }}>
                  {department.members ? department.members.length : 0}
                </td>
                <td style={{ padding: "12px" }}>
                  {department.created_at
                    ? new Date(department.created_at).toLocaleDateString(
                        "vi-VN"
                      )
                    : "-"}
                </td>
                <td style={{ padding: "12px" }}>
                  <button
                    onClick={() => handleEdit(department)}
                    style={{
                      marginRight: "5px",
                      padding: "5px 10px",
                      background: "#ffc107",
                      border: "none",
                      borderRadius: "3px",
                      cursor: "pointer",
                    }}
                  >
                    Sửa
                  </button>
                  <button
                    onClick={() => handleDelete(department.id)}
                    style={{
                      padding: "5px 10px",
                      background: "#dc3545",
                      color: "white",
                      border: "none",
                      borderRadius: "3px",
                      cursor: "pointer",
                    }}
                  >
                    Xóa
                  </button>
                  <button
                    onClick={() => assignLead(department.id)}
                    style={{
                      padding: "5px 10px",
                      background: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "3px",
                      cursor: "pointer",
                      marginLeft: "5px",
                    }}
                  >
                    Bổ nhiệm Lead
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {departments.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#6c757d" }}>
          <p>Chưa có phòng ban nào. Hãy tạo phòng ban đầu tiên!</p>
        </div>
      )}
    </div>
  );
}
