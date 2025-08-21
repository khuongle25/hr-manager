import React, { useState } from 'react';
import api from '../api/axios';

export default function Register() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [message, setMessage] = useState('');

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await api.post('/register/', form);
      setMessage('Đăng ký thành công! Hãy đăng nhập.');
    } catch (err) {
      setMessage('Lỗi đăng ký: ' + (err.response?.data?.detail || ''));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Đăng ký</h2>
      <input name="username" placeholder="Username" value={form.username} onChange={handleChange} required />
      <input name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
      <input name="first_name" placeholder="Họ" value={form.first_name} onChange={handleChange} />
      <input name="last_name" placeholder="Tên" value={form.last_name} onChange={handleChange} />
      <input name="password" type="password" placeholder="Mật khẩu" value={form.password} onChange={handleChange} required />
      <button type="submit">Đăng ký</button>
      {message && <div>{message}</div>}
    </form>
  );
}