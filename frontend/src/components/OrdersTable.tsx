import React, { useEffect, useState } from 'react';
import { getWarehouseData } from '../api';

const OrdersTable: React.FC = () => {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWarehouseData(1).then(data => {
      setOrders(data.orders);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading orders...</div>;

  return (
    <div>
      <h2>Orders</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Customer</th>
            <th>Priority</th>
            <th>Created</th>
            <th>Deadline</th>
            <th>Status</th>
            <th>Items</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => (
            <tr key={order.id}>
              <td>{order.id}</td>
              <td>{order.customer_name || order.customer}</td>
              <td>{order.priority}</td>
              <td>{new Date(order.created_at).toLocaleString()}</td>
              <td>{new Date(order.shipping_deadline).toLocaleString()}</td>
              <td>{order.status}</td>
              <td>{order.items.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrdersTable; 