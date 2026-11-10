import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api";

export default function RegistroEgresado() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    nombre: "",
    apellido: "",
    carrera: "",
    anio_egreso: "",
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
      const datos = {
        ...form,
        anio_egreso: form.anio_egreso ? Number(form.anio_egreso) : null,
      };
      const usuario = await api.registrarEgresado(datos);
      navigate(`/perfil-egresado?usuario_id=${usuario.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="contenedor" style={{ maxWidth: 480 }}>
      <h1>Crea tu cuenta de egresado</h1>
      <p style={{ color: "var(--color-muted)" }}>
        ¿Tienes una empresa? <Link to="/registro/empresa">Regístrala aquí</Link>.
      </p>

      <form onSubmit={enviar} className="tarjeta">
        <div className="campo">
          <label htmlFor="nombre">Nombre</label>
          <input
            id="nombre"
            required
            value={form.nombre}
            onChange={(e) => actualizar("nombre", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="apellido">Apellido</label>
          <input
            id="apellido"
            required
            value={form.apellido}
            onChange={(e) => actualizar("apellido", e.target.value)}
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
          <label htmlFor="carrera">Carrera</label>
          <input
            id="carrera"
            value={form.carrera}
            onChange={(e) => actualizar("carrera", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="anio">Año de egreso</label>
          <input
            id="anio"
            type="number"
            min="1990"
            max="2100"
            value={form.anio_egreso}
            onChange={(e) => actualizar("anio_egreso", e.target.value)}
          />
        </div>

        {error && <p className="mensaje-error">{error}</p>}

        <button type="submit" className="boton boton-primario" disabled={cargando}>
          {cargando ? "Creando cuenta…" : "Crear cuenta"}
        </button>
      </form>
    </div>
  );
}
