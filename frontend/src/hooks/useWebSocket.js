import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = 'ws://localhost:8000/ws';
const RECONNECT_DELAY = 3000;

/**
 * Custom hook for WebSocket connection to the backend.
 * Handles auto-reconnect and exposes the latest payload.
 */
export function useWebSocket() {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      console.log('[WS] Connected');
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setData(payload);
      } catch (err) {
        console.warn('[WS] Parse error:', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('[WS] Disconnected — reconnecting in', RECONNECT_DELAY, 'ms');
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
    };

    ws.onerror = (err) => {
      console.error('[WS] Error:', err);
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { data, connected };
}
