import { formatNumber } from '../utils/pollutionCalc';

/**
 * Real-time traffic counts panel showing per-class vehicle counts.
 */
export default function TrafficPanel({ trafficData }) {
    const counts = trafficData?.counts || {};
    const total = trafficData?.total || 0;
    const fps = trafficData?.fps || 0;

    const vehicles = [
        { key: 'car', icon: '🚗', label: 'Cars', color: '#00e676' },
        { key: 'motorcycle', icon: '🏍️', label: 'Motorcycles', color: '#ff9100' },
        { key: 'bus', icon: '🚌', label: 'Buses', color: '#448aff' },
        { key: 'truck', icon: '🚛', label: 'Trucks', color: '#ff5252' },
    ];

    return (
        <div className="panel traffic-panel">
            <div className="panel-header">
                <span className="panel-icon">🚦</span>
                <h3>Traffic Monitor</h3>
                <span className="fps-badge">{fps} FPS</span>
            </div>

            <div className="total-count">
                <span className="total-number">{formatNumber(total)}</span>
                <span className="total-label">vehicles detected</span>
            </div>

            <div className="vehicle-grid">
                {vehicles.map((v) => (
                    <div key={v.key} className="vehicle-card" style={{ '--accent': v.color }}>
                        <span className="vehicle-icon">{v.icon}</span>
                        <span className="vehicle-count">{formatNumber(counts[v.key] || 0)}</span>
                        <span className="vehicle-label">{v.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
