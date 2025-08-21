import axios from "axios";

export const sendMessageToAI = async (userId, role, message, token) => {
  const res = await axios.post("http://localhost:9000/chat", {
    user_id: userId,
    role: role,
    message: message,
    token: token,
  });
  return res.data;
};
