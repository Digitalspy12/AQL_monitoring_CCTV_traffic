/**
 * Live annotated video feed from the AI detector.
 * Receives base64 JPEG frames pushed via WebSocket.
 */
export default function VideoFeed({ frameBase64 }) {
    return (
        <div className="panel video-panel">
            <div className="panel-header">
                <span className="panel-icon">📹</span>
                <h3>Live Detection Feed</h3>
                <span className={`live-dot ${frameBase64 ? 'active' : ''}`} />
            </div>
            <div className="video-wrapper">
                {frameBase64 ? (
                    <img
                        src={`data:image/jpeg;base64,${frameBase64}`}
                        alt="Live AI Detection"
                        className="video-frame"
                    />
                ) : (
                    <div className="video-placeholder">
                        <div className="placeholder-icon">📡</div>
                        <p>Waiting for video feed…</p>
                        <p className="placeholder-sub">
                            Ensure the backend is running and a video source is configured.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
