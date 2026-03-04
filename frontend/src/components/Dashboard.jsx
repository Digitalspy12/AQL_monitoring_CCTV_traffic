import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import MapView from './MapView';
import TrafficPanel from './TrafficPanel';
import PollutionPanel from './PollutionPanel';
import VideoFeed from './VideoFeed';
import StatsChart from './StatsChart';

/**
 * Main dashboard layout — orchestrates all sub-panels.
 */
export default function Dashboard() {
    const { data, connected } = useWebSocket();
    const [history, setHistory] = useState([]);
    const historyRef = useRef([]);

    // Accumulate traffic snapshots for the chart
    useEffect(() => {
        if (data?.traffic) {
            const entry = {
                timestamp: data.timestamp,
                counts: data.traffic.counts,
            };
            historyRef.current = [...historyRef.current.slice(-59), entry];
            setHistory([...historyRef.current]);
        }
    }, [data]);

    return (
        <div className="dashboard">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <h1 className="logo">
                        <span className="logo-icon">🏙️</span>
                        Digital Twin
                    </h1>
                    <span className="subtitle">Smart City Monitoring</span>
                </div>
                <div className="header-right">
                    <div className={`connection-status ${connected ? 'online' : 'offline'}`}>
                        <span className="status-dot" />
                        {connected ? 'Live' : 'Offline'}
                    </div>
                    <div className="timestamp">
                        {data?.timestamp
                            ? new Date(data.timestamp).toLocaleTimeString()
                            : '--:--:--'}
                    </div>
                </div>
            </header>

            {/* Main Grid */}
            <main className="dashboard-grid">
                {/* Left column */}
                <div className="grid-left">
                    <VideoFeed frameBase64={data?.frame} />
                    <StatsChart history={history} />
                </div>

                {/* Center — Map */}
                <div className="grid-center">
                    <MapView
                        heatmapPoints={data?.pollution?.heatmap_points}
                        center={[28.6139, 77.209]}
                        zoom={13}
                    />
                </div>

                {/* Right column */}
                <div className="grid-right">
                    <TrafficPanel trafficData={data?.traffic} />
                    <PollutionPanel pollutionData={data?.pollution} />
                </div>
            </main>
        </div>
    );
}
