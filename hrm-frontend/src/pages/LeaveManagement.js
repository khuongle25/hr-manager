import React, { useState, useEffect } from "react";
import api from "../api/axios";

export default function LeaveManagement({ user }) {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    leave_type: "",
    start_date: "",
    end_date: "",
    reason: "",
  });

  useEffect(() => {
    fetchLeaveRequests();
    fetchLeaveTypes();
  }, []);

  const fetchLeaveRequests = async () => {
    try {
      const response = await api.get("/leave-requests/");
      setLeaveRequests(response.data.results || []);
    } catch (error) {
      console.error("Lỗi khi tải danh sách đơn nghỉ phép:", error);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        leave_type_id: formData.leave_type,
      };
      delete submitData.leave_type;

      await api.post("/leave-requests/", submitData);
      setShowForm(false);
      setFormData({
        leave_type: "",
        start_date: "",
        end_date: "",
        reason: "",
      });
      fetchLeaveRequests();
    } catch (error) {
      console.error("Lỗi khi tạo đơn nghỉ phép:", error);
      if (error.response?.data) {
        console.error("Chi tiết lỗi:", error.response.data);
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleApprove = async (requestId) => {
    try {
      await api.post(`/leave-requests/${requestId}/approve/`);
      fetchLeaveRequests();
    } catch (error) {
      console.error("Lỗi khi duyệt đơn:", error);
    }
  };

  const handleDeny = async (requestId) => {
    try {
      await api.post(`/leave-requests/${requestId}/deny/`);
      fetchLeaveRequests();
    } catch (error) {
      console.error("Lỗi khi từ chối đơn:", error);
    }
  };

  const handleChangeDecision = async (requestId, newStatus) => {
    const statusText = newStatus === "approved" ? "Duyệt" : "Từ chối";
    if (
      !window.confirm(
        `Bạn có chắc chắn muốn đổi quyết định thành "${statusText}"?`
      )
    ) {
      return;
    }

    try {
      await api.post(`/leave-requests/${requestId}/change_decision/`, {
        status: newStatus,
      });
      fetchLeaveRequests();
    } catch (error) {
      console.error("Lỗi khi thay đổi quyết định:", error);
    }
  };

  const getStatusLabel = (request) => {
    if (
      request.team_lead_status === "denied" ||
      request.hr_status === "denied"
    ) {
      return { label: "Từ chối", color: "#dc3545" };
    }
    if (
      request.team_lead_status === "approved" &&
      request.hr_status === "approved"
    ) {
      return { label: "Đã duyệt", color: "#28a745" };
    }
    return { label: "Chờ duyệt", color: "#ffc107" };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("vi-VN");
  };

  const getPageTitle = () => {
    if (user?.role === "hr") return "Quản lý Nghỉ phép (Toàn công ty)";
    if (user?.role === "team_lead") return "Quản lý Nghỉ phép (Team)";
    return "Đơn nghỉ phép của tôi";
  };

  const canApprove = (request) => {
    if (user?.role === "hr") return true;
    if (user?.role === "team_lead") {
      const leads = request.employee?.department?.lead || [];
      return Array.isArray(leads) && leads.some((l) => l.id === user.id);
    }
    return false;
  };

  const canChangeDecision = canApprove;

  // Hàm kiểm tra trạng thái chờ duyệt tổng hợp
  const isPending = (request) => {
    return (
      request.team_lead_status !== "denied" &&
      request.hr_status !== "denied" &&
      !(
        request.team_lead_status === "approved" &&
        request.hr_status === "approved"
      )
    );
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
        {(user?.role === "employee" ||
          user?.role === "hr" ||
          user?.role === "team_lead") && (
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
            {showForm ? "Hủy" : "Tạo đơn nghỉ phép"}
          </button>
        )}
      </div>

      {(user?.role === "employee" ||
        user?.role === "hr" ||
        user?.role === "team_lead") &&
        showForm && (
          <div
            style={{
              background: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            <h3>Tạo đơn nghỉ phép mới</h3>
            <form onSubmit={handleSubmit}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "15px",
                }}
              >
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
                  name="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={handleChange}
                  required
                  style={{
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #ddd",
                  }}
                />
                <input
                  name="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={handleChange}
                  required
                  style={{
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #ddd",
                  }}
                />
              </div>
              <textarea
                name="reason"
                placeholder="Lý do nghỉ phép"
                value={formData.reason}
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
                  Gửi đơn
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
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
              {(user?.role === "hr" || user?.role === "team_lead") && (
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
                Loại nghỉ
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Từ ngày
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Đến ngày
              </th>
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Số ngày
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
              <th
                style={{
                  padding: "12px",
                  textAlign: "left",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Lý do
              </th>
              {(user?.role === "hr" || user?.role === "team_lead") && (
                <th
                  style={{
                    padding: "12px",
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                  }}
                >
                  Thao tác
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {leaveRequests.map((request) => {
              const startDate = new Date(request.start_date);
              const endDate = new Date(request.end_date);
              const daysDiff =
                Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
              const status = getStatusLabel(request);

              return (
                <tr key={request.id} style={{ borderBottom: "1px solid #eee" }}>
                  {(user?.role === "hr" || user?.role === "team_lead") && (
                    <td style={{ padding: "12px" }}>
                      {request.employee?.full_name}
                    </td>
                  )}
                  <td style={{ padding: "12px" }}>
                    {request.leave_type?.name}
                  </td>
                  <td style={{ padding: "12px" }}>
                    {formatDate(request.start_date)}
                  </td>
                  <td style={{ padding: "12px" }}>
                    {formatDate(request.end_date)}
                  </td>
                  <td style={{ padding: "12px" }}>{daysDiff} ngày</td>
                  <td style={{ padding: "12px" }}>
                    <span
                      style={{
                        padding: "4px 8px",
                        borderRadius: "4px",
                        background: status.color,
                        color: "white",
                        fontSize: "12px",
                      }}
                    >
                      {status.label}
                    </span>
                  </td>
                  <td style={{ padding: "12px", maxWidth: "200px" }}>
                    <div
                      style={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {request.reason}
                    </div>
                  </td>
                  {(user?.role === "hr" || user?.role === "team_lead") && (
                    <td style={{ padding: "12px" }}>
                      {isPending(request) && canApprove(request) && (
                        <div style={{ display: "flex", gap: "10px" }}>
                          {/* Nếu user là HR và hr_status là pending */}
                          {user?.role === "hr" &&
                            request.hr_status === "pending" && (
                              <>
                                <button
                                  onClick={() => handleApprove(request.id)}
                                  style={{
                                    padding: "8px 16px",
                                    background: "#28a745",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                  }}
                                >
                                  Duyệt
                                </button>
                                <button
                                  onClick={() => handleDeny(request.id)}
                                  style={{
                                    padding: "8px 16px",
                                    background: "#dc3545",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                  }}
                                >
                                  Từ chối
                                </button>
                              </>
                            )}
                          {/* Nếu user là team_lead và team_lead_status là pending */}
                          {user?.role === "team_lead" &&
                            request.team_lead_status === "pending" && (
                              <>
                                <button
                                  onClick={() => handleApprove(request.id)}
                                  style={{
                                    padding: "8px 16px",
                                    background: "#28a745",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                  }}
                                >
                                  Duyệt
                                </button>
                                <button
                                  onClick={() => handleDeny(request.id)}
                                  style={{
                                    padding: "8px 16px",
                                    background: "#dc3545",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                  }}
                                >
                                  Từ chối
                                </button>
                              </>
                            )}
                          {/* Nếu user đã quyết định, cho phép đổi ý */}
                          {user?.role === "hr" &&
                            request.hr_status !== "pending" && (
                              <>
                                {request.hr_status === "denied" && (
                                  <button
                                    onClick={() =>
                                      handleChangeDecision(
                                        request.id,
                                        "approved"
                                      )
                                    }
                                    style={{
                                      padding: "8px 16px",
                                      background: "#28a745",
                                      color: "white",
                                      border: "none",
                                      borderRadius: "4px",
                                      cursor: "pointer",
                                    }}
                                  >
                                    Đổi thành Duyệt
                                  </button>
                                )}
                                {request.hr_status === "approved" && (
                                  <button
                                    onClick={() =>
                                      handleChangeDecision(request.id, "denied")
                                    }
                                    style={{
                                      padding: "8px 16px",
                                      background: "#dc3545",
                                      color: "white",
                                      border: "none",
                                      borderRadius: "4px",
                                      cursor: "pointer",
                                    }}
                                  >
                                    Đổi thành Từ chối
                                  </button>
                                )}
                              </>
                            )}
                          {user?.role === "team_lead" &&
                            request.team_lead_status !== "pending" && (
                              <>
                                {request.team_lead_status === "denied" && (
                                  <button
                                    onClick={() =>
                                      handleChangeDecision(
                                        request.id,
                                        "approved"
                                      )
                                    }
                                    style={{
                                      padding: "8px 16px",
                                      background: "#28a745",
                                      color: "white",
                                      border: "none",
                                      borderRadius: "4px",
                                      cursor: "pointer",
                                    }}
                                  >
                                    Đổi thành Duyệt
                                  </button>
                                )}
                                {request.team_lead_status === "approved" && (
                                  <button
                                    onClick={() =>
                                      handleChangeDecision(request.id, "denied")
                                    }
                                    style={{
                                      padding: "8px 16px",
                                      background: "#dc3545",
                                      color: "white",
                                      border: "none",
                                      borderRadius: "4px",
                                      cursor: "pointer",
                                    }}
                                  >
                                    Đổi thành Từ chối
                                  </button>
                                )}
                              </>
                            )}
                        </div>
                      )}
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {leaveRequests.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#6c757d" }}>
          <p>Chưa có đơn nghỉ phép nào.</p>
        </div>
      )}
    </div>
  );
}
