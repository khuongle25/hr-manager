import React, { useState } from "react";
import { sendMessageToAI } from "../services/ai_send";

export default function AIChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const token = localStorage.getItem("access");
  const userId = localStorage.getItem("user_id") || 1;
  const role = localStorage.getItem("role") || "employee";

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    const aiRes = await sendMessageToAI(userId, role, input, token);
    setMessages((msgs) => [
      ...msgs,
      {
        sender: "ai",
        text: aiRes.user_message,
        result: aiRes.result,
        intent: aiRes.intent,
        entities: aiRes.entities,
      },
    ]);
    setInput("");
  };

  // Hàm render chi tiết kết quả nếu là thông tin cá nhân
  const renderResult = (msg) => {
    if (msg.intent === "view_profile" && msg.result && msg.result.full_name) {
      return (
        <div
          style={{
            fontSize: 14,
            marginTop: 4,
            background: "#f6f6f6",
            padding: 8,
            borderRadius: 6,
          }}
        >
          <div>
            <b>Họ tên:</b> {msg.result.full_name}
          </div>
          <div>
            <b>Email:</b> {msg.result.email}
          </div>
          <div>
            <b>Vai trò:</b> {msg.result.role}
          </div>
        </div>
      );
    }
    // Có thể mở rộng cho các intent khác (ví dụ: request_leave, add_employee...)
    return null;
  };

  return (
    <div
      style={{
        maxWidth: 480,
        margin: "40px auto",
        padding: 24,
        background: "#fff",
        borderRadius: 12,
        boxShadow: "0 2px 12px #0001",
      }}
    >
      <h2 style={{ textAlign: "center", color: "#1976d2" }}>AI ASSISTANT</h2>
      <div
        style={{
          border: "1px solid #e0e0e0",
          minHeight: 240,
          padding: 16,
          marginBottom: 16,
          borderRadius: 8,
          background: "#fafbfc",
          overflowY: "auto",
          maxHeight: 400,
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              margin: "12px 0",
            }}
          >
            <div
              style={{
                display: "inline-block",
                background: msg.sender === "user" ? "#1976d2" : "#f1f1f1",
                color: msg.sender === "user" ? "#fff" : "#222",
                borderRadius: 16,
                padding: "10px 18px",
                maxWidth: 320,
                wordBreak: "break-word",
                boxShadow:
                  msg.sender === "user"
                    ? "0 2px 8px #1976d233"
                    : "0 2px 8px #0001",
              }}
            >
              <b>{msg.sender === "user" ? "Bạn" : "AI"}:</b> {msg.text}
            </div>
            {msg.sender === "ai" && renderResult(msg)}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
            fontSize: 16,
          }}
          placeholder="Nhập tin nhắn..."
        />
        <button
          onClick={handleSend}
          style={{
            background: "#1976d2",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "0 24px",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Gửi
        </button>
      </div>
    </div>
  );
}
