import { getAqiColor } from '../utils/pollutionCalc';

/**
 * Pollution panel showing AQI gauge and noise level.
 */
export default function PollutionPanel({ pollutionData }) {
    const aqi = pollutionData?.aqi ?? 0;
    const noise = pollutionData?.noise_db ?? 0;
    const category = pollutionData?.category || 'N/A';
    const color = getAqiColor(category);

    // AQI gauge: arc from 0 to 500
    const percentage = Math.min(100, (aqi / 500) * 100);

    return (
        <div className="panel pollution-panel">
            <div className="panel-header">
                <span className="panel-icon">🌿</span>
                <h3>Environment</h3>
            </div>

            {/* AQI Gauge */}
            <div className="aqi-section">
                <div className="aqi-gauge">
                    <svg viewBox="0 0 120 70" className="gauge-svg">
                        {/* Background arc */}
                        <path
                            d="M 10 65 A 50 50 0 0 1 110 65"
                            fill="none"
                            stroke="rgba(255,255,255,0.1)"
                            strokeWidth="8"
                            strokeLinecap="round"
                        />
                        {/* Value arc */}
                        <path
                            d="M 10 65 A 50 50 0 0 1 110 65"
                            fill="none"
                            stroke={color}
                            strokeWidth="8"
                            strokeLinecap="round"
                            strokeDasharray={`${percentage * 1.57} 157`}
                            className="gauge-arc"
                        />
                    </svg>
                    <div className="aqi-value" style={{ color }}>
                        {Math.round(aqi)}
                    </div>
                    <div className="aqi-label">AQI</div>
                </div>
                <div className="aqi-category" style={{ color }}>
                    {category}
                </div>
            </div>

            {/* Noise Level */}
            <div className="noise-section">
                <div className="noise-header">
                    <span className="noise-icon">🔊</span>
                    <span>Noise Level</span>
                </div>
                <div className="noise-bar-container">
                    <div
                        className="noise-bar"
                        style={{
                            width: `${Math.min(100, (noise / 130) * 100)}%`,
                            background: noise > 85
                                ? 'linear-gradient(90deg, #ff9100, #ff0000)'
                                : 'linear-gradient(90deg, #00e676, #ffff00)',
                        }}
                    />
                </div>
                <div className="noise-value">{noise.toFixed(1)} dB</div>
            </div>
        </div>
    );
}
