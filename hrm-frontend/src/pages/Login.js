import React, { useState } from 'react';
import api from '../api/axios';

export default function Login({ setToken }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await api.post('/login/', form);
      setToken(res.data.access); // Lưu access token vào state/parent
      localStorage.setItem('access', res.data.access);
      localStorage.setItem('refresh', res.data.refresh);
      setMessage('Đăng nhập thành công!');
    } catch (err) {
      setMessage('Sai tài khoản hoặc mật khẩu!');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Đăng nhập</h2>
      <input name="username" placeholder="Username" value={form.username} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Mật khẩu" value={form.password} onChange={handleChange} required />
      <button type="submit">Đăng nhập</button>
      {message && <div>{message}</div>}
    </form>
  );
}