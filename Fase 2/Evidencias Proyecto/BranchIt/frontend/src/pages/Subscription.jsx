import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";
import "./Account.css";

export default function Subscription() {
  const [status, setStatus] = useState(null), [error, setError] = useState("");
  const errorRef = useRef(null);
  useEffect(() => {
    let active = true;
    api.billing().then((data) => { if (active) setStatus(data); }).catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, []);
  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);
  return <section className="contenedor dashboard account-page"><WorkspaceNav /><h1>Mi suscripción</h1>
    {error && <p ref={errorRef} tabIndex={-1} role="alert" className="mensaje-error">{error}</p>}
    {!status && !error && <p role="status">Cargando suscripción…</p>}
    {status && <div className="account-grid"><article className="tarjeta"><h2>Plan gratuito</h2><p className="subscription-price">$0</p>
      <ul><li>Portafolio profesional.</li><li>Consulta de ofertas y postulaciones según tu acceso.</li><li>Orientación con IA y una entrevista de práctica diaria.</li></ul>
    </article><article className="tarjeta employment-summary"><h2>Suscripción BranchIT</h2>
      <p className="subscription-price">{new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(status.precio_clp)} <span>/ mes</span></p>
      <ul>{status.beneficios.map((benefit) => <li key={benefit}>{benefit}</li>)}</ul>
      <p>La IA depende de la disponibilidad y las cuotas del proveedor. La suscripción no evita los bloqueos por contratación o por un año de experiencia.</p>
      <p><strong>Estado: {status.estado === "activa" ? "Activa" : "Sin suscripción activa"}</strong></p>
      {status.vigente_hasta && <p>Vigente hasta {new Intl.DateTimeFormat("es-CL", { dateStyle: "long" }).format(new Date(status.vigente_hasta))}.</p>}
      <p role="status">Webpay · Configuración pendiente</p><button className="boton boton-primario" type="button" disabled>Pago no disponible</button>
      <p>No se realizan cobros ni se activa una suscripción desde esta pantalla mientras la pasarela esté pendiente.</p>
    </article></div>}
  </section>;
}
