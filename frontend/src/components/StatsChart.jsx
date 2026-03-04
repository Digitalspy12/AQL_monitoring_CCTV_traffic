import { useMemo } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from 'recharts';

/**
 * Time-series chart showing recent traffic counts.
 * Maintains a rolling window of data points.
 */
export default function StatsChart({ history }) {
    const chartData = useMemo(() => {
        if (!history || history.length === 0) return [];
        return history
            .slice(-30)
            .map((entry, i) => ({
                time: entry.timestamp
                    ? new Date(entry.timestamp).toLocaleTimeString()
                    : `T-${30 - i}`,
                Cars: entry.counts?.car || entry.car_count || 0,
                Buses: entry.counts?.bus || entry.bus_count || 0,
                Motos: entry.counts?.motorcycle || entry.motorcycle_count || 0,
                Trucks: entry.counts?.truck || entry.truck_count || 0,
            }));
    }, [history]);

    return (
        <div className="panel chart-panel">
            <div className="panel-header">
                <span className="panel-icon">📊</span>
                <h3>Traffic Trends</h3>
            </div>
            <div className="chart-wrapper">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorCars" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#00e676" stopOpacity={0.4} />
                                    <stop offset="95%" stopColor="#00e676" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorBuses" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#448aff" stopOpacity={0.4} />
                                    <stop offset="95%" stopColor="#448aff" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorMotos" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ff9100" stopOpacity={0.4} />
                                    <stop offset="95%" stopColor="#ff9100" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorTrucks" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ff5252" stopOpacity={0.4} />
                                    <stop offset="95%" stopColor="#ff5252" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                            <XAxis
                                dataKey="time"
                                tick={{ fill: '#888', fontSize: 10 }}
                                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                            />
                            <YAxis
                                tick={{ fill: '#888', fontSize: 10 }}
                                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    background: 'rgba(20,20,30,0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                    color: '#fff',
                                }}
                            />
                            <Legend wrapperStyle={{ color: '#ccc', fontSize: 12 }} />
                            <Area type="monotone" dataKey="Cars" stroke="#00e676" fill="url(#colorCars)" />
                            <Area type="monotone" dataKey="Buses" stroke="#448aff" fill="url(#colorBuses)" />
                            <Area type="monotone" dataKey="Motos" stroke="#ff9100" fill="url(#colorMotos)" />
                            <Area type="monotone" dataKey="Trucks" stroke="#ff5252" fill="url(#colorTrucks)" />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="chart-placeholder">
                        <p>Collecting data…</p>
                    </div>
                )}
            </div>
        </div>
    );
}
