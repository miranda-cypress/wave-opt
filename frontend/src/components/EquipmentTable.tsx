import React, { useEffect, useState } from 'react';
import { getWarehouseData } from '../api';

const EquipmentTable: React.FC = () => {
  const [equipment, setEquipment] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWarehouseData(1).then(data => {
      setEquipment(data.equipment);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading equipment...</div>;

  return (
    <div>
      <h2>Equipment</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Capacity</th>
            <th>Hourly Cost</th>
            <th>Efficiency</th>
          </tr>
        </thead>
        <tbody>
          {equipment.map(eq => (
            <tr key={eq.id}>
              <td>{eq.name}</td>
              <td>{eq.equipment_type}</td>
              <td>{eq.capacity}</td>
              <td>${eq.hourly_cost.toFixed(2)}</td>
              <td>{eq.efficiency_factor}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EquipmentTable; 