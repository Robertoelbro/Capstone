import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api";

export default function RegistroEmpresa() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    nombre_empresa: "",
    rubro: "",
    descripcion: "",
    sitio_web: "",
  });
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  function actualizar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function enviar(e) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    try {
      const usuario = await api.registrarEmpresa(form);
      navigate(`/ofertas-empresa?usuario_id=${usuario.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="contenedor" style={{ maxWidth: 480 }}>
      <h1>Registra tu empresa</h1>
      <p style={{ color: "var(--color-muted)" }}>
        ¿Eres egresado? <Link to="/registro/egresado">Crea tu cuenta aquí</Link>.
      </p>

      <form onSubmit={enviar} className="tarjeta">
        <div className="campo">
          <label htmlFor="nombre_empresa">Nombre de la empresa</label>
          <input
            id="nombre_empresa"
            required
            value={form.nombre_empresa}
            onChange={(e) => actualizar("nombre_empresa", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="email">Correo</label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => actualizar("email", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => actualizar("password", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="rubro">Rubro</label>
          <input
            id="rubro"
            value={form.rubro}
            onChange={(e) => actualizar("rubro", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="sitio_web">Sitio web</label>
          <input
            id="sitio_web"
            value={form.sitio_web}
            onChange={(e) => actualizar("sitio_web", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="descripcion">Descripción breve</label>
          <textarea
            id="descripcion"
            rows={3}
            value={form.descripcion}
            onChange={(e) => actualizar("descripcion", e.target.value)}
          />
        </div>

        {error && <p className="mensaje-error">{error}</p>}

        <button type="submit" className="boton boton-primario" disabled={cargando}>
          {cargando ? "Creando cuenta…" : "Registrar empresa"}
        </button>
      </form>
    </div>
  );
}
