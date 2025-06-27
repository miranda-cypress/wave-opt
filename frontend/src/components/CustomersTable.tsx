import React, { useEffect, useState } from 'react';
import { getWarehouseData } from '../api';

const CustomersTable: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWarehouseData(1).then(data => {
      setCustomers(data.customers || []);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading customers...</div>;

  return (
    <div>
      <h2>Customers</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Order Freq</th>
            <th>Avg Order Value</th>
            <th>Priority</th>
            <th>Deadline Pref</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((c, idx) => (
            <tr key={idx}>
              <td>{c.name}</td>
              <td>{c.customer_type}</td>
              <td>{c.order_frequency?.toFixed(2)}</td>
              <td>${c.avg_order_value?.toFixed(2)}</td>
              <td>{c.priority_tendency}</td>
              <td>{c.deadline_preference}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomersTable; 