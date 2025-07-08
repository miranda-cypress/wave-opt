import React, { useState, useEffect } from 'react';
import { getWarehouseData } from '../api';
import './SKUDetails.css';

interface SKUDetailsProps {
  onNavigate: (page: string) => void;
}

interface SKU {
  id: number;
  warehouse_id: number;
  sku_code: string;
  name: string;
  category: string;
  zone: string;
  pick_time_minutes: number;
  pack_time_minutes: number;
  volume_cubic_feet: number;
  weight_lbs: number;
  demand_pattern: string;
  velocity_class: string;
  shelf_life_days?: number;
  external_sku_id?: string;
  source_id?: number;
  import_id?: number;
  augmentation_id?: number;
  created_at: string;
  updated_at: string;
}

const SKUDetails: React.FC<SKUDetailsProps> = ({ onNavigate }) => {
  const [skus, setSKUs] = useState<SKU[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedZone, setSelectedZone] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    loadSKUData();
  }, []);

  const loadSKUData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getWarehouseData(1);
      setSKUs(data.skus || []);
    } catch (err) {
      setError('Failed to load SKU data');
      console.error('Error loading SKU data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getUniqueCategories = () => {
    const categories = [...new Set(skus.map(sku => sku.category))];
    return categories.sort();
  };

  const getUniqueZones = () => {
    const zones = [...new Set(skus.map(sku => sku.zone))];
    return zones.sort();
  };

  const filterAndSortSKUs = () => {
    let filtered = skus.filter(sku => {
      const categoryMatch = selectedCategory === 'all' || sku.category === selectedCategory;
      const zoneMatch = selectedZone === 'all' || sku.zone === selectedZone;
      return categoryMatch && zoneMatch;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      let aValue: any = a[sortBy as keyof SKU];
      let bValue: any = b[sortBy as keyof SKU];

      // Handle string comparison
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const getSortIcon = (column: string) => {
    if (sortBy !== column) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="sku-details-page">
        <div className="loading-message">Loading SKU Details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sku-details-page">
        <div className="error-message">
          <h2>Error Loading SKU Data</h2>
          <p>{error}</p>
          <button onClick={loadSKUData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const filteredSKUs = filterAndSortSKUs();
  const categories = getUniqueCategories();
  const zones = getUniqueZones();

  return (
    <div className="sku-details-page">
      <div className="wave-selector-section">
        <div className="wave-header">
          <h1 className="wave-title">SKU Details</h1>
        </div>

        <div className="filters-section">
          <div className="filter-group">
            <label htmlFor="category-filter">Category:</label>
            <select
              id="category-filter"
              className="wave-dropdown"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="zone-filter">Zone:</label>
            <select
              id="zone-filter"
              className="wave-dropdown"
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
            >
              <option value="all">All Zones</option>
              {zones.map(zone => (
                <option key={zone} value={zone}>Zone {zone}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-by">Sort by:</label>
            <select
              id="sort-by"
              className="wave-dropdown"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="name">Name</option>
              <option value="sku_code">SKU Code</option>
              <option value="category">Category</option>
              <option value="zone">Zone</option>
              <option value="pick_time_minutes">Pick Time</option>
              <option value="pack_time_minutes">Pack Time</option>
              <option value="weight_lbs">Weight</option>
              <option value="volume_cubic_feet">Volume</option>
              <option value="velocity_class">Velocity Class</option>
            </select>
          </div>
        </div>

        <div className="quick-stats-grid">
          <div className="quick-stat">
            <div className="stat-icon">📦</div>
            <div className="stat-label">Total SKUs</div>
            <div className="stat-after">{filteredSKUs.length}</div>
          </div>
          <div className="quick-stat">
            <div className="stat-icon">🏷️</div>
            <div className="stat-label">Categories</div>
            <div className="stat-after">{categories.length}</div>
          </div>
          <div className="quick-stat">
            <div className="stat-icon">📍</div>
            <div className="stat-label">Zones</div>
            <div className="stat-after">{zones.length}</div>
          </div>
          <div className="quick-stat">
            <div className="stat-icon">⏱️</div>
            <div className="stat-label">Avg Pick Time</div>
            <div className="stat-after">
              {filteredSKUs.length > 0 ? 
                (filteredSKUs.reduce((sum, sku) => sum + sku.pick_time_minutes, 0) / filteredSKUs.length).toFixed(1) + ' min' : 
                'N/A'}
            </div>
          </div>
        </div>
      </div>

      <div className="comparison-section">
        <div className="current-method">
          <h3 className="method-title">SKU Inventory</h3>
          
          <div className="sku-table-container">
            <table className="sku-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('sku_code')} className="sortable">
                    SKU Code {getSortIcon('sku_code')}
                  </th>
                  <th onClick={() => handleSort('name')} className="sortable">
                    Name {getSortIcon('name')}
                  </th>
                  <th onClick={() => handleSort('category')} className="sortable">
                    Category {getSortIcon('category')}
                  </th>
                  <th onClick={() => handleSort('zone')} className="sortable">
                    Zone {getSortIcon('zone')}
                  </th>
                  <th onClick={() => handleSort('pick_time_minutes')} className="sortable">
                    Pick Time {getSortIcon('pick_time_minutes')}
                  </th>
                  <th onClick={() => handleSort('pack_time_minutes')} className="sortable">
                    Pack Time {getSortIcon('pack_time_minutes')}
                  </th>
                  <th onClick={() => handleSort('weight_lbs')} className="sortable">
                    Weight {getSortIcon('weight_lbs')}
                  </th>
                  <th onClick={() => handleSort('volume_cubic_feet')} className="sortable">
                    Volume {getSortIcon('volume_cubic_feet')}
                  </th>
                  <th onClick={() => handleSort('velocity_class')} className="sortable">
                    Velocity {getSortIcon('velocity_class')}
                  </th>
                  <th onClick={() => handleSort('demand_pattern')} className="sortable">
                    Demand Pattern {getSortIcon('demand_pattern')}
                  </th>
                  <th>Shelf Life</th>
                  <th>External ID</th>
                </tr>
              </thead>
              <tbody>
                {filteredSKUs.map(sku => (
                  <tr key={sku.id}>
                    <td className="sku-code">{sku.sku_code}</td>
                    <td className="sku-name">{sku.name}</td>
                    <td className="sku-category">{sku.category}</td>
                    <td className="sku-zone">Zone {sku.zone}</td>
                    <td className="sku-pick-time">{sku.pick_time_minutes} min</td>
                    <td className="sku-pack-time">{sku.pack_time_minutes} min</td>
                    <td className="sku-weight">{sku.weight_lbs} lbs</td>
                    <td className="sku-volume">{sku.volume_cubic_feet} ft³</td>
                    <td className="sku-velocity">{sku.velocity_class}</td>
                    <td className="sku-demand">{sku.demand_pattern}</td>
                    <td className="sku-shelf-life">
                      {sku.shelf_life_days ? `${sku.shelf_life_days} days` : 'N/A'}
                    </td>
                    <td className="sku-external-id">
                      {sku.external_sku_id || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredSKUs.length === 0 && (
            <div className="no-data-message">
              <p>No SKUs found matching the selected filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SKUDetails; 