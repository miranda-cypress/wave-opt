import React, { useEffect, useState } from 'react';
import { getWarehouseData } from '../api';

const SKUsTable: React.FC = () => {
  const [skus, setSKUs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWarehouseData(1).then(data => {
      setSKUs(data.skus);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading SKUs...</div>;

  return (
    <div>
      <h2>SKUs</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Zone</th>
            <th>Pick Time</th>
            <th>Pack Time</th>
            <th>Volume</th>
            <th>Weight</th>
            <th>Demand</th>
          </tr>
        </thead>
        <tbody>
          {skus.map(sku => (
            <tr key={sku.id}>
              <td>{sku.name}</td>
              <td>{sku.category}</td>
              <td>{sku.zone}</td>
              <td>{sku.pick_time_minutes}</td>
              <td>{sku.pack_time_minutes}</td>
              <td>{sku.volume_cubic_feet}</td>
              <td>{sku.weight_lbs}</td>
              <td>{sku.demand_pattern}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SKUsTable; 