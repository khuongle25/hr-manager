import React, { useEffect, useState } from 'react';
import api from '../api/axios';

export default function LeaveRequestPage() {
  const [requests, setRequests] = useState([]);
  const [form, setForm] = useState({ start_date: '', end_date: '', reason: '', leave_type: 1 });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    const res = await api.get('/leave-requests/');
    setRequests(res.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/leave-requests/', form);
      setMessage('Gửi đơn thành công!');
      fetchRequests();
    } catch (err) {
      setMessage('Lỗi gửi đơn!');
    }
  };

  const handleApprove = async (id) => {
    await api.post(`/leave-requests/${id}/approve/`);
    fetchRequests();
  };

  const handleDeny = async (id) => {
    await api.post(`/leave-requests/${id}/deny/`);
    fetchRequests();
  };

  return (
    <div>
      <h2>Gửi đơn nghỉ phép</h2>
      <form onSubmit={handleSubmit}>
        <input type="date" value={form.start_date} onChange={e => setForm({...form, start_date: e.target.value})} />
        <input type="date" value={form.end_date} onChange={e => setForm({...form, end_date: e.target.value})} />
        <input value={form.reason} onChange={e => setForm({...form, reason: e.target.value})} placeholder="Lý do" />
        <input value={form.leave_type} onChange={e => setForm({...form, leave_type: e.target.value})} placeholder="ID loại phép" />
        <button type="submit">Gửi đơn</button>
      </form>
      {message && <div>{message}</div>}
      <h3>Danh sách đơn nghỉ phép</h3>
      <table border="1">
        <thead>
          <tr>
            <th>ID</th><th>Ngày bắt đầu</th><th>Ngày kết thúc</th><th>Lý do</th><th>Trạng thái</th><th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          {requests.map(r => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.start_date}</td>
              <td>{r.end_date}</td>
              <td>{r.reason}</td>
              <td>{r.status}</td>
              <td>
                {r.status === 'pending' && (
                  <>
                    <button onClick={() => handleApprove(r.id)}>Duyệt</button>
                    <button onClick={() => handleDeny(r.id)}>Từ chối</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}