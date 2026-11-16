const ORDER = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// Only this internal receipt route may survive an expired session.
export function safeSubscriptionReturn(value) {
  if (typeof value !== "string") return null;
  if (value === "/suscripcion") return value;
  if (!value.startsWith("/suscripcion?") || value.includes("#")) return null;
  const query = new URLSearchParams(value.slice("/suscripcion?".length));
  const order = query.get("orden");
  if ([...query.keys()].length !== 1 || !order || !ORDER.test(order)) return null;
  return `/suscripcion?orden=${order}`;
}
