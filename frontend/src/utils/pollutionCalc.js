/**
 * AQI category → color mapping for the dashboard.
 */
export const AQI_COLORS = {
    'Good': '#00e400',
    'Moderate': '#ffff00',
    'Unhealthy for Sensitive Groups': '#ff7e00',
    'Unhealthy': '#ff0000',
    'Very Unhealthy': '#8f3f97',
    'Hazardous': '#7e0023',
};

/**
 * Return the color for a given AQI category.
 */
export function getAqiColor(category) {
    return AQI_COLORS[category] || '#888';
}

/**
 * Format a number with commas.
 */
export function formatNumber(n) {
    return n != null ? n.toLocaleString() : '—';
}
