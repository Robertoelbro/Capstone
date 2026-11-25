const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// One atomic record keeps an idempotency key bound to its own server order.
// The separately stored last receipt must never retire another pending attempt.
export function readPaymentAttempt(storage, key) {
  try {
    const raw = storage.getItem(key);
    if (!raw) return null;
    // Preserve earlier UUID-only sessions conservatively until checkout links them.
    if (UUID.test(raw)) return { request_id: raw, order_id: null };
    const value = JSON.parse(raw);
    if (!value || typeof value !== "object" || !UUID.test(value.request_id || "")) return null;
    if (value.order_id !== null && !UUID.test(value.order_id || "")) return null;
    return { request_id: value.request_id, order_id: value.order_id };
  } catch { return null; }
}

export function beginPaymentAttempt(storage, key, requestId) {
  if (!UUID.test(requestId || "")) throw new Error("La referencia del intento de pago no es válida.");
  const value = { request_id: requestId, order_id: null };
  storage.setItem(key, JSON.stringify(value));
  return value;
}

export function linkPaymentOrder(storage, key, requestId, orderId) {
  if (!UUID.test(orderId || "")) throw new Error("La referencia de la orden no es válida.");
  const current = readPaymentAttempt(storage, key);
  if (!current || current.request_id !== requestId) return false;
  if (current.order_id && current.order_id !== orderId) return false;
  storage.setItem(key, JSON.stringify({ request_id: requestId, order_id: orderId }));
  return true;
}

export function retirePaymentAttempt(storage, key, orderId) {
  const current = readPaymentAttempt(storage, key);
  if (!current || current.order_id !== orderId) return false;
  try { storage.removeItem(key); return true; }
  catch { return false; }
}
