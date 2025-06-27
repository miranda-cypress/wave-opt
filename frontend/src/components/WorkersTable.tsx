import React, { useEffect, useState } from 'react';
import { getWarehouseData } from '../api';

const WorkersTable: React.FC = () => {
  const [workers, setWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWarehouseData(1).then(data => {
      setWorkers(data.workers);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading workers...</div>;

  return (
    <div>
      <h2>Workers</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Skills</th>
            <th>Hourly Rate</th>
            <th>Efficiency</th>
            <th>Max Hours/Day</th>
          </tr>
        </thead>
        <tbody>
          {workers.map(worker => (
            <tr key={worker.id}>
              <td>{worker.name}</td>
              <td>{worker.skills.join(', ')}</td>
              <td>${worker.hourly_rate.toFixed(2)}</td>
              <td>{worker.efficiency_factor}</td>
              <td>{worker.max_hours_per_day}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WorkersTable; 