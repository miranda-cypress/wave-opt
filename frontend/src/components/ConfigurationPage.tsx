import React, { useState, useEffect } from 'react';
import { getConfiguration, updateConfiguration, resetConfiguration, updateDemoDates } from '../api';
import './ConfigurationPage.css';

interface ConfigurationPageProps {
  onNavigate: (page: string) => void;
}

interface ConfigData {
  walking_time: {
    walking_speed_fpm: number;
    vertical_movement_weight: number;
    zone_change_penalty_minutes: number;
    level_change_penalty_minutes: number;
    x_weight: number;
    y_weight: number;
  };
  optimization: {
    default_hourly_rate: number;
    estimated_minutes_per_order: number;
    efficiency_threshold_low: number;
    efficiency_threshold_high: number;
  };
  standard_times: {
    label_minutes_per_order: number;
    stage_minutes_per_order: number;
    ship_minutes_per_order: number;
    consolidate_minutes_per_item: number;
    pack_minutes_per_item: number;
    pick_minutes_per_item: number;
  };
}

const ConfigurationPage: React.FC<ConfigurationPageProps> = ({ onNavigate }) => {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getConfiguration();
      setConfig(response.config);
    } catch (err) {
      setError('Failed to load configuration');
      console.error('Error loading configuration:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await updateConfiguration(config);
      setSuccess('Configuration saved successfully');
      setEditing(false);
    } catch (err) {
      setError('Failed to save configuration');
      console.error('Error saving configuration:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      await resetConfiguration();
      await loadConfiguration();
      setSuccess('Configuration reset to defaults');
      setEditing(false);
    } catch (err) {
      setError('Failed to reset configuration');
      console.error('Error resetting configuration:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDemoData = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const result = await updateDemoDates();
      setSuccess(result.message);
    } catch (err) {
      setError('Failed to update demo data');
      console.error('Error updating demo data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (section: keyof ConfigData, field: string, value: string | number) => {
    if (!config) return;

    setConfig({
      ...config,
      [section]: {
        ...config[section],
        [field]: typeof value === 'string' ? parseFloat(value) || 0 : value
      }
    });
  };

  if (loading) {
    return (
      <div className="configuration-page">
        <div className="loading-message">Loading configuration...</div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="configuration-page">
        <div className="error-message">
          <h2>Error Loading Configuration</h2>
          <p>{error}</p>
          <button onClick={loadConfiguration} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="configuration-page">
      <div className="page-header">
        <h1>Configuration</h1>
        <p>Manage application settings and parameters</p>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {success && (
        <div className="success-message">
          <p>{success}</p>
        </div>
      )}

      <div className="config-sections">
        {/* Walking Time Configuration */}
        <div className="config-section">
          <h2>Walking Time Parameters</h2>
          <p>Configure walking time calculation parameters used for optimization.</p>
          
          <div className="config-grid">
            <div className="config-item">
              <label htmlFor="walking_speed">Walking Speed (feet per minute):</label>
              <input
                type="number"
                id="walking_speed"
                value={config.walking_time.walking_speed_fpm}
                onChange={(e) => handleInputChange('walking_time', 'walking_speed_fpm', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
              <span className="description">Average walking speed for warehouse workers</span>
            </div>

            <div className="config-item">
              <label htmlFor="vertical_weight">Vertical Movement Weight:</label>
              <input
                type="number"
                id="vertical_weight"
                value={config.walking_time.vertical_movement_weight}
                onChange={(e) => handleInputChange('walking_time', 'vertical_movement_weight', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
              <span className="description">Multiplier for vertical movement (stairs/elevators)</span>
            </div>

            <div className="config-item">
              <label htmlFor="zone_penalty">Zone Change Penalty (minutes):</label>
              <input
                type="number"
                id="zone_penalty"
                value={config.walking_time.zone_change_penalty_minutes}
                onChange={(e) => handleInputChange('walking_time', 'zone_change_penalty_minutes', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
              <span className="description">Additional time penalty for changing zones</span>
            </div>

            <div className="config-item">
              <label htmlFor="level_penalty">Level Change Penalty (minutes):</label>
              <input
                type="number"
                id="level_penalty"
                value={config.walking_time.level_change_penalty_minutes}
                onChange={(e) => handleInputChange('walking_time', 'level_change_penalty_minutes', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
              <span className="description">Additional time penalty for changing levels</span>
            </div>
          </div>
        </div>

        {/* Optimization Configuration */}
        <div className="config-section">
          <h2>Optimization Parameters</h2>
          <p>Configure default values used in optimization calculations.</p>
          
          <div className="config-grid">
            <div className="config-item">
              <label htmlFor="hourly_rate">Default Hourly Rate ($):</label>
              <input
                type="number"
                id="hourly_rate"
                value={config.optimization.default_hourly_rate}
                onChange={(e) => handleInputChange('optimization', 'default_hourly_rate', e.target.value)}
                disabled={!editing}
                step="0.01"
                min="0"
              />
              <span className="description">Default hourly rate for cost calculations</span>
            </div>

            <div className="config-item">
              <label htmlFor="minutes_per_order">Estimated Minutes per Order:</label>
              <input
                type="number"
                id="minutes_per_order"
                value={config.optimization.estimated_minutes_per_order}
                onChange={(e) => handleInputChange('optimization', 'estimated_minutes_per_order', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
              <span className="description">Default time estimate for processing an order</span>
            </div>

            <div className="config-item">
              <label htmlFor="efficiency_low">Low Efficiency Threshold (%):</label>
              <input
                type="number"
                id="efficiency_low"
                value={config.optimization.efficiency_threshold_low}
                onChange={(e) => handleInputChange('optimization', 'efficiency_threshold_low', e.target.value)}
                disabled={!editing}
                step="1"
                min="0"
                max="100"
              />
              <span className="description">Efficiency threshold for high risk assessment</span>
            </div>

            <div className="config-item">
              <label htmlFor="efficiency_high">High Efficiency Threshold (%):</label>
              <input
                type="number"
                id="efficiency_high"
                value={config.optimization.efficiency_threshold_high}
                onChange={(e) => handleInputChange('optimization', 'efficiency_threshold_high', e.target.value)}
                disabled={!editing}
                step="1"
                min="0"
                max="100"
              />
              <span className="description">Efficiency threshold for low risk assessment</span>
            </div>
          </div>
        </div>

        {/* Standard Times Configuration */}
        <div className="config-section">
          <h2>Standard Times</h2>
          <p>Configure standard times for each order and item stage.</p>
          <div className="config-grid">
            <div className="config-item">
              <label htmlFor="label_minutes_per_order">Label (minutes per order):</label>
              <input
                type="number"
                id="label_minutes_per_order"
                value={config.standard_times.label_minutes_per_order}
                onChange={(e) => handleInputChange('standard_times', 'label_minutes_per_order', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
            </div>
            <div className="config-item">
              <label htmlFor="stage_minutes_per_order">Stage (minutes per order):</label>
              <input
                type="number"
                id="stage_minutes_per_order"
                value={config.standard_times.stage_minutes_per_order}
                onChange={(e) => handleInputChange('standard_times', 'stage_minutes_per_order', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
            </div>
            <div className="config-item">
              <label htmlFor="ship_minutes_per_order">Ship (minutes per order):</label>
              <input
                type="number"
                id="ship_minutes_per_order"
                value={config.standard_times.ship_minutes_per_order}
                onChange={(e) => handleInputChange('standard_times', 'ship_minutes_per_order', e.target.value)}
                disabled={!editing}
                step="0.1"
                min="0"
              />
            </div>
            <div className="config-item">
              <label htmlFor="consolidate_minutes_per_item">Consolidate (minutes per item):</label>
              <input
                type="number"
                id="consolidate_minutes_per_item"
                value={config.standard_times.consolidate_minutes_per_item}
                onChange={(e) => handleInputChange('standard_times', 'consolidate_minutes_per_item', e.target.value)}
                disabled={!editing}
                step="0.01"
                min="0"
              />
            </div>
            <div className="config-item">
              <label htmlFor="pack_minutes_per_item">Pack (minutes per item):</label>
              <input
                type="number"
                id="pack_minutes_per_item"
                value={config.standard_times.pack_minutes_per_item}
                onChange={(e) => handleInputChange('standard_times', 'pack_minutes_per_item', e.target.value)}
                disabled={!editing}
                step="0.01"
                min="0"
              />
            </div>
            <div className="config-item">
              <label htmlFor="pick_minutes_per_item">Pick (minutes per item):</label>
              <input
                type="number"
                id="pick_minutes_per_item"
                value={config.standard_times.pick_minutes_per_item}
                onChange={(e) => handleInputChange('standard_times', 'pick_minutes_per_item', e.target.value)}
                disabled={!editing}
                step="0.01"
                min="0"
              />
            </div>
          </div>
        </div>

        {/* Demo Data Management */}
        <div className="config-section">
          <h2>Demo Data Management</h2>
          <p>Update demo data dates to ensure they start from tomorrow.</p>
          
          <div className="demo-data-actions">
            <button 
              className="btn btn-info"
              onClick={handleUpdateDemoData}
              disabled={loading}
            >
              {loading ? 'Updating...' : 'Update Demo Data'}
            </button>
            <span className="description">
              This will move all demo orders and wave plans forward to start tomorrow
            </span>
          </div>
        </div>

      </div>

      <div className="config-actions">
        {!editing ? (
          <button 
            className="btn btn-primary"
            onClick={() => setEditing(true)}
          >
            Edit Configuration
          </button>
        ) : (
          <div className="action-buttons">
            <button 
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => {
                setEditing(false);
                loadConfiguration(); // Reload to discard changes
              }}
              disabled={saving}
            >
              Cancel
            </button>
          </div>
        )}
        
        <button 
          className="btn btn-warning"
          onClick={handleReset}
          disabled={saving || editing}
        >
          Reset to Defaults
        </button>
      </div>
    </div>
  );
};

export default ConfigurationPage; 