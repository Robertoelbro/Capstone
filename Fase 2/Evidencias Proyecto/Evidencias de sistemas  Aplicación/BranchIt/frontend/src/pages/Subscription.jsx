import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useSession } from "../session";
import { beginPaymentAttempt, linkPaymentOrder, readPaymentAttempt, retirePaymentAttempt } from "../billingAttempt";
import WorkspaceNav from "../Components/WorkspaceNav";
import "./Account.css";
import "./Subscription.css";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const FINAL_STATES = new Set(["autorizada", "rechazada", "cancelada", "expirada"]);
const money = (value) => new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
const dateLabel = (value) => new Intl.DateTimeFormat("es-CL", { dateStyle: "long", timeZone: "America/Santiago" }).format(new Date(value));

function storedReference(key) {
  try {
    const value = sessionStorage.getItem(key);
    return value && UUID.test(value) ? value : null;
  } catch { return null; }
}

function sessionStore() {
  try { return window.sessionStorage; }
  catch { return null; }
}

function orderMessage(order, active) {
  switch (order.estado) {
    case "autorizada": return order.beneficio_aplicado && active
      ? "Pago de prueba autorizado. Tu suscripción está activa."
      : "Pago autorizado. Consultaremos la vigencia confirmada por el servidor.";
    case "rechazada": return "Webpay rechazó el pago. Esta operación no activó una suscripción.";
    case "cancelada": return "El pago fue cancelado. Esta operación no activó una suscripción.";
    case "expirada": return "El pago venció. Puedes iniciar una nueva operación.";
    case "incierta": return "Todavía no se pudo confirmar el resultado. Revisa esta operación antes de intentar un nuevo pago.";
    case "creando": return "La operación se está preparando. Conservamos su referencia para reintentar sin duplicarla.";
    default: return "Pago pendiente de confirmación. La suscripción se activa únicamente cuando el servidor valida el resultado.";
  }
}

export default function Subscription() {
  const { user } = useSession();
  const location = useLocation();
  const navigate = useNavigate();
  const requestKey = `branchit-webpay-request-${user.id}`;
  const orderKey = `branchit-webpay-order-${user.id}`;
  const [status, setStatus] = useState(null);
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [orderError, setOrderError] = useState("");
  const [checking, setChecking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [newOrderConfirmed, setNewOrderConfirmed] = useState(false);
  const [reload, setReload] = useState(0);
  const [orderId, setOrderId] = useState(() => {
    const query = new URLSearchParams(location.search).get("orden");
    return query && UUID.test(query) ? query : storedReference(orderKey);
  });
  const requestId = useRef(readPaymentAttempt(sessionStore(), requestKey)?.request_id || null);
  const sending = useRef(false);
  const mounted = useRef(true);
  const errorRef = useRef(null);
  const receiptRef = useRef(null);
  const returnHasQuery = useRef(new URLSearchParams(location.search).has("orden"));

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  useEffect(() => {
    function restore(event) {
      if (!event.persisted) return;
      sending.current = false;
      setBusy(false);
      setChecking(false);
      setReload((value) => value + 1);
    }
    window.addEventListener("pageshow", restore);
    return () => window.removeEventListener("pageshow", restore);
  }, []);

  // Only an opaque order ID is retained. Webpay tokens never enter URLs or storage.
  useEffect(() => {
    const query = new URLSearchParams(location.search).get("orden");
    if (!query) return;
    if (UUID.test(query)) {
      setOrderId(query);
      try { sessionStorage.setItem(orderKey, query); } catch { /* The receipt can still be read in this page. */ }
    } else {
      setOrderError("La referencia de pago no es válida.");
    }
    navigate("/suscripcion", { replace: true });
  }, [location.search, navigate, orderKey]);

  useEffect(() => {
    let active = true;
    setError("");
    api.billing()
      .then((data) => { if (active) setStatus(data); })
      .catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [reload]);

  useEffect(() => {
    if (!orderId) return;
    let active = true;
    setChecking(true);
    setOrderError("");
    api.billingOrder(orderId).then(async (value) => {
      if (!active) return;
      setOrder(value);
      if (FINAL_STATES.has(value.estado)) {
        if (retirePaymentAttempt(sessionStore(), requestKey, value.order_id)) requestId.current = null;
      }
      const account = await api.billing();
      if (active) setStatus(account);
    }).catch((err) => { if (active) setOrderError(err.message); })
      .finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, [orderId, requestKey, reload]);

  useEffect(() => { if (error || orderError) errorRef.current?.focus(); }, [error, orderError]);
  useEffect(() => {
    if (order && !checking && returnHasQuery.current) {
      receiptRef.current?.focus();
      returnHasQuery.current = false;
    }
  }, [order, checking]);

  function keepOrder(id) {
    if (!UUID.test(id || "")) throw new Error("El servidor no devolvió una referencia de pago válida.");
    if (!linkPaymentOrder(sessionStorage, requestKey, requestId.current, id)) {
      throw new Error("No pudimos vincular esta orden con el intento actual. Revisa su estado antes de continuar.");
    }
    try { sessionStorage.setItem(orderKey, id); } catch { /* request_id is already retained for retry. */ }
    if (mounted.current) setOrderId(id);
  }

  async function checkout() {
    if (sending.current || !status?.pago_habilitado || status.entorno !== "integration" || !status.modo_prueba) return;
    sending.current = true;
    let redirecting = false;
    setBusy(true);
    setError("");
    try {
      // Preserve the same idempotency key on failed requests and reloads.
      if (!requestId.current) {
        if (!window.crypto?.randomUUID) throw new Error("Este navegador no permite iniciar un pago seguro. Usa un navegador actualizado.");
        const id = window.crypto.randomUUID();
        try { beginPaymentAttempt(sessionStorage, requestKey, id); }
        catch { throw new Error("Necesitamos conservar la referencia de esta operación en la sesión del navegador. Permite el almacenamiento de sesión antes de continuar."); }
        requestId.current = id;
      }
      const payment = await api.billingCheckout(requestId.current);
      keepOrder(payment.order_id);
      if (!payment.url || !payment.token) {
        // An idempotent retry may find a transaction already completed.
        const value = await api.billingOrder(payment.order_id);
        if (mounted.current) setOrder(value);
        if (FINAL_STATES.has(value.estado)) {
          if (retirePaymentAttempt(sessionStore(), requestKey, value.order_id)) requestId.current = null;
        }
        const account = await api.billing();
        if (mounted.current) setStatus(account);
        return;
      }
      const url = new URL(payment.url);
      if (payment.entorno !== "integration" || url.href !== "https://webpay3gint.transbank.cl/webpayserver/initTransaction" || !/^[a-f0-9]{64}$/i.test(payment.token)) {
        throw new Error("No pudimos validar el destino de Webpay. No se enviaron datos de pago.");
      }
      const form = document.createElement("form");
      form.method = "POST";
      form.action = url.href;
      form.hidden = true;
      const token = document.createElement("input");
      token.type = "hidden";
      token.name = "token_ws";
      token.value = payment.token;
      form.append(token);
      document.body.append(form);
      try { HTMLFormElement.prototype.submit.call(form); redirecting = true; }
      finally { form.remove(); }
    } catch (err) {
      if (mounted.current) setError(err.message || "No pudimos iniciar el pago. Puedes reintentar la misma operación.");
    } finally {
      if (!redirecting) {
        sending.current = false;
        if (mounted.current) setBusy(false);
      }
    }
  }

  async function startNewOrder() {
    if (!newOrderConfirmed || sending.current || order?.estado !== "incierta" || order.puede_reconciliar) return;
    try {
      sessionStorage.removeItem(requestKey);
      sessionStorage.removeItem(orderKey);
    } catch {
      setError("No pudimos actualizar la referencia de la sesión. No se inició otra operación.");
      return;
    }
    requestId.current = null;
    setOrderId(null);
    setOrder(null);
    setNewOrderConfirmed(false);
    await checkout();
  }

  async function refreshOrder() {
    if (!orderId || sending.current) return;
    sending.current = true;
    setChecking(true);
    setError("");
    setOrderError("");
    try {
      const value = order?.puede_reconciliar
        ? await api.reconcileBillingOrder(orderId)
        : await api.billingOrder(orderId);
      if (!mounted.current) return;
      setOrder(value);
      if (FINAL_STATES.has(value.estado)) {
        if (retirePaymentAttempt(sessionStore(), requestKey, value.order_id)) requestId.current = null;
      }
      const account = await api.billing();
      if (mounted.current) setStatus(account);
    } catch (err) { if (mounted.current) setOrderError(err.message); }
    finally { sending.current = false; if (mounted.current) setChecking(false); }
  }

  const paymentReady = status?.pago_habilitado && status.entorno === "integration" && status.modo_prueba;
  const pendingOrder = order && !FINAL_STATES.has(order.estado);
  return <section className="contenedor dashboard account-page subscription-page">
    <WorkspaceNav /><h1>Mi suscripción</h1>
    {(error || orderError) && <p ref={errorRef} tabIndex={-1} role="alert" className="mensaje-error">{error || orderError}</p>}
    {!status && !error && <p role="status">Cargando suscripción…</p>}
    {!status && error && <button className="boton boton-secundario" type="button" onClick={() => setReload((value) => value + 1)}>Reintentar</button>}
    {status?.modo_prueba && <p className="subscription-test" role="note"><strong>Modo integración</strong> · Pagos de prueba, sin cobros reales.</p>}
    {orderId && <section className="tarjeta subscription-receipt" aria-labelledby="payment-result-heading">
      <h2 id="payment-result-heading" tabIndex={-1} ref={receiptRef}>Resultado del pago</h2>
      {checking && <p role="status">Consultando el estado confirmado por el servidor…</p>}
      {order && <>
        <p role="status">{orderMessage(order, status?.estado === "activa")}</p>
        <dl><dt>Referencia</dt><dd>{order.order_id}</dd><dt>Monto</dt><dd>{money(order.precio_clp)}</dd></dl>
        {order.vigente_hasta && order.beneficio_aplicado && <p>Vigencia confirmada hasta {dateLabel(order.vigente_hasta)}.</p>}
      </>}
      <button className="boton boton-secundario" type="button" onClick={refreshOrder} disabled={checking || busy}>{checking ? "Consultando…" : "Actualizar estado del pago"}</button>
      {order?.estado === "incierta" && !order.puede_reconciliar && <div className="subscription-new-operation">
        <p>No se obtuvo una transacción de Webpay que podamos consultar. Puedes iniciar otra operación de prueba con una referencia nueva.</p>
        <label><input type="checkbox" checked={newOrderConfirmed} disabled={busy || checking} onChange={(event) => setNewOrderConfirmed(event.target.checked)} />Quiero crear una nueva operación de prueba.</label>
        <button type="button" className="boton boton-secundario" disabled={!newOrderConfirmed || busy || checking || !paymentReady} onClick={startNewOrder}>Crear nueva operación</button>
      </div>}
    </section>}
    {status && <div className="account-grid"><article className="tarjeta"><h2>Plan gratuito</h2><p className="subscription-price">$0</p>
      <ul><li>Portafolio profesional.</li><li>Consulta de ofertas y postulaciones según tu acceso.</li><li>Orientación con IA y una entrevista de práctica diaria.</li></ul>
    </article><article className="tarjeta employment-summary"><h2>Suscripción BranchIT</h2>
      <p className="subscription-price">{money(status.precio_clp)} <span>/ mes</span></p>
      <ul>{status.beneficios.map((benefit) => <li key={benefit}>{benefit}</li>)}</ul>
      <p>Renovación manual por un mes, sin cargos automáticos.</p>
      <p>La IA depende de la disponibilidad y las cuotas del proveedor. La suscripción no evita los bloqueos por contratación o por un año de experiencia.</p>
      <p><strong>Estado: {status.estado === "activa" ? "Activa" : "Sin suscripción activa"}</strong></p>
      {status.vigente_hasta && <p>Vigente hasta {dateLabel(status.vigente_hasta)}.</p>}
      <p>{paymentReady ? "Webpay de prueba disponible" : "Webpay · Configuración pendiente"}</p>
      <button className="boton boton-primario" type="button" onClick={checkout} disabled={!paymentReady || busy || checking || (!!orderId && !order && !orderError)} aria-describedby="subscription-payment-help">
        {busy ? "Preparando Webpay…" : !paymentReady ? "Pago no disponible" : pendingOrder ? "Retomar pago de prueba" : status.estado === "activa" ? "Renovar un mes con Webpay" : "Suscribirme con Webpay"}
      </button>
      <p id="subscription-payment-help" className="muted">{paymentReady ? "Continuarás en Webpay. La activación depende de la confirmación del pago en el servidor." : "Los pagos permanecen deshabilitados hasta completar la configuración de integración."}</p>
    </article></div>}
  </section>;
}
