import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Dynamically import leaflet.heat (it attaches to L)
import 'leaflet.heat';

/**
 * Inner component that manages the heatmap layer.
 */
function HeatmapLayer({ points }) {
    const map = useMap();
    const heatRef = useRef(null);

    useEffect(() => {
        if (!points || points.length === 0) return;

        const heatData = points.map((p) => [p.lat, p.lng, p.intensity]);

        if (heatRef.current) {
            heatRef.current.setLatLngs(heatData);
        } else {
            heatRef.current = L.heatLayer(heatData, {
                radius: 30,
                blur: 25,
                maxZoom: 17,
                max: 1.0,
                gradient: {
                    0.0: '#00ff00',
                    0.3: '#adff2f',
                    0.5: '#ffff00',
                    0.7: '#ff8c00',
                    0.9: '#ff0000',
                    1.0: '#8b0000',
                },
            }).addTo(map);
        }

        return () => {
            // Do not remove on re-render, just update data
        };
    }, [points, map]);

    return null;
}

/**
 * Interactive map with OpenStreetMap tiles and a dynamic heatmap overlay.
 */
export default function MapView({ heatmapPoints, center, zoom = 13 }) {
    const defaultCenter = center || [28.6139, 77.209];

    return (
        <div className="map-container">
            <div className="panel-header">
                <span className="panel-icon">🗺️</span>
                <h3>Pollution Heatmap</h3>
            </div>
            <MapContainer
                center={defaultCenter}
                zoom={zoom}
                style={{ height: '100%', width: '100%', borderRadius: '0 0 12px 12px', minHeight: '360px' }}
                scrollWheelZoom={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                <HeatmapLayer points={heatmapPoints} />
            </MapContainer>
        </div>
    );
}
