import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiBell, FiBriefcase, FiX } from 'react-icons/fi';
import { api } from '../../api';
import './Notifications.css';

export default function Notifications() {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const root = useRef(null);
  const button = useRef(null);
  const alive = useRef(false);
  const inFlight = useRef(false);
  const location = useLocation();
  const refresh = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      const result = await api.notifications();
      if (alive.current) { setData(result); setError(''); }
    } catch (err) {
      if (alive.current) setError(err.message);
    } finally { inFlight.current = false; }
  }, []);
  useEffect(() => {
    alive.current = true;
    const check = () => { if (!document.hidden) refresh(); };
    check();
    const timer = window.setInterval(check, 30000);
    window.addEventListener('focus', check);
    document.addEventListener('visibilitychange', check);
    return () => {
      alive.current = false;
      clearInterval(timer);
      window.removeEventListener('focus', check);
      document.removeEventListener('visibilitychange', check);
    };
  }, [refresh]);
  useEffect(() => { setOpen(false); }, [location.pathname]);
  useEffect(() => {
    if (!open) return;
    const close = (event) => { if (!root.current?.contains(event.target)) setOpen(false); };
    document.addEventListener('pointerdown', close);
    return () => document.removeEventListener('pointerdown', close);
  }, [open]);
  async function markRead(id) {
    setBusy(true);
    try {
      if (id) await api.readNotification(id);
      else await api.readAllNotifications();
      await refresh();
    } catch (err) { if (alive.current) setError(err.message); }
    finally { if (alive.current) setBusy(false); }
  }
  const count = data?.sin_leer || 0;
  return <div className="notifications" ref={root} onKeyDown={(event) => {
    if (event.key === 'Escape') { setOpen(false); button.current?.focus(); event.stopPropagation(); }
  }}>
    <button type="button" className="notification-bell" ref={button}
      aria-label={`Notificaciones${count ? `: ${count} sin leer` : ''}`}
      aria-expanded={open} aria-controls="notifications-panel"
      onClick={() => { setOpen(!open); if (!open) refresh(); }}>
      <FiBell aria-hidden="true" />
      {count > 0 && <span className="notification-count" aria-hidden="true">{count > 99 ? '99+' : count}</span>}
    </button>
    {open && <section id="notifications-panel" className="notifications-panel" aria-label="Notificaciones">
      <div className="notifications-heading"><h2>Notificaciones</h2>
        <button type="button" aria-label="Cerrar notificaciones" onClick={() => { setOpen(false); button.current?.focus(); }}><FiX /></button>
      </div>
      {count > 0 && <button type="button" className="notifications-read-all" disabled={busy} onClick={() => markRead()}>Marcar todas como leídas</button>}
      {error && <div className="notifications-feedback" role="alert"><p>{error}</p><button type="button" onClick={refresh}>Reintentar</button></div>}
      {!data && !error && <p className="notifications-feedback" role="status">Cargando…</p>}
      {data?.items.length === 0 && <p className="notifications-feedback">No tienes notificaciones.</p>}
      {data?.items.length > 0 && <ul className="notifications-list">{data.items.map(item => <li key={item.id} className={item.leida ? '' : 'is-unread'}>
        <Link to={item.destino} onClick={() => { setOpen(false); if (!item.leida) markRead(item.id); }}>
          <span className="notification-icon"><FiBriefcase aria-hidden="true" /></span>
          <span><span className="notification-message">{item.mensaje}</span><time dateTime={`${item.creada}Z`}>{new Date(`${item.creada}Z`).toLocaleString('es-CL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</time></span>
          {!item.leida && <span className="notification-dot" aria-label="Sin leer" />}
        </Link>
      </li>)}</ul>}
    </section>}
  </div>;
}
