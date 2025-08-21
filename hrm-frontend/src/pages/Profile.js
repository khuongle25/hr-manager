import React, { useEffect, useState } from "react";
import api from "../api/axios";

export default function Profile({ user }) {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    address: "",
    date_of_birth: "",
  });
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone: user.phone || "",
        address: user.address || "",
        date_of_birth: user.date_of_birth || "",
      });
    }
  }, [user]);

  if (!user) return <div>Hãy đăng nhập để xem profile.</div>;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess("");
    setError("");
    try {
      await api.patch(`/users/${user.id}/`, formData);
      setSuccess("Cập nhật thành công!");
      setEditing(false);
    } catch (err) {
      setError("Cập nhật thất bại!");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setEditing(true);
    setSuccess("");
    setError("");
  };

  const handleCancel = () => {
    setEditing(false);
    setFormData({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      phone: user.phone || "",
      address: user.address || "",
      date_of_birth: user.date_of_birth || "",
    });
    setSuccess("");
    setError("");
  };

  return (
    <div
      style={{
        maxWidth: 500,
        margin: "40px auto",
        background: "#f8f9fa",
        padding: 24,
        borderRadius: 10,
        boxShadow: "0 2px 8px #eee",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: 24 }}>
        Thông tin cá nhân
      </h2>
      <div style={{ marginBottom: 16 }}>
        <strong>Email:</strong> {user.email}
      </div>
      <div style={{ marginBottom: 16 }}>
        <strong>Mã nhân viên:</strong> {user.employee_id}
      </div>
      {!editing ? (
        <>
          <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
            <div style={{ flex: 1 }}>
              <label>Họ</label>
              <div
                style={{
                  padding: 8,
                  background: "#fff",
                  borderRadius: 4,
                  border: "1px solid #ccc",
                }}
              >
                {formData.first_name}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <label>Tên</label>
              <div
                style={{
                  padding: 8,
                  background: "#fff",
                  borderRadius: 4,
                  border: "1px solid #ccc",
                }}
              >
                {formData.last_name}
              </div>
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Số điện thoại</label>
            <div
              style={{
                padding: 8,
                background: "#fff",
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            >
              {formData.phone}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Địa chỉ</label>
            <div
              style={{
                padding: 8,
                background: "#fff",
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            >
              {formData.address}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Ngày sinh</label>
            <div
              style={{
                padding: 8,
                background: "#fff",
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            >
              {formData.date_of_birth}
            </div>
          </div>
          {success && (
            <div style={{ color: "green", marginBottom: 12 }}>{success}</div>
          )}
          {error && (
            <div style={{ color: "red", marginBottom: 12 }}>{error}</div>
          )}
          <div style={{ display: "flex", justifyContent: "center", gap: 12 }}>
            <button
              type="button"
              onClick={handleEdit}
              style={{
                padding: "8px 24px",
                background: "#007bff",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Chỉnh sửa
            </button>
          </div>
        </>
      ) : (
        <form onSubmit={handleSubmit} autoComplete="off">
          <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
            <div style={{ flex: 1 }}>
              <label>Họ</label>
              <input
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: 8,
                  borderRadius: 4,
                  border: "1px solid #ccc",
                }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label>Tên</label>
              <input
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: 8,
                  borderRadius: 4,
                  border: "1px solid #ccc",
                }}
              />
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Số điện thoại</label>
            <input
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: 8,
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Địa chỉ</label>
            <input
              name="address"
              value={formData.address}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: 8,
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Ngày sinh</label>
            <input
              name="date_of_birth"
              type="date"
              value={formData.date_of_birth || ""}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: 8,
                borderRadius: 4,
                border: "1px solid #ccc",
              }}
            />
          </div>
          {success && (
            <div style={{ color: "green", marginBottom: 12 }}>{success}</div>
          )}
          {error && (
            <div style={{ color: "red", marginBottom: 12 }}>{error}</div>
          )}
          <div style={{ display: "flex", justifyContent: "center", gap: 12 }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: "8px 24px",
                background: "#28a745",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              {loading ? "Đang lưu..." : "Lưu"}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              style={{
                padding: "8px 24px",
                background: "#dc3545",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Hủy
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
