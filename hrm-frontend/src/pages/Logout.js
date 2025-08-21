import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Logout({ handleLogout }) {
  const navigate = useNavigate();

  useEffect(() => {
    handleLogout(); // Cập nhật state ở App.js
    navigate("/login", { replace: true });
  }, [handleLogout, navigate]);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "50vh",
        flexDirection: "column",
      }}
    >
      <h2>Đang đăng xuất...</h2>
      <p>Bạn sẽ được chuyển đến trang đăng nhập.</p>
    </div>
  );
}
