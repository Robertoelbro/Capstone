import JobFacts from "../Components/JobFacts";
import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import {
  FiArrowUpRight,
  FiBriefcase,
  FiMapPin,
  FiSearch,
  FiArrowRight,
} from "react-icons/fi";
import { api } from "../api";
import { useSession } from "../session";
import WorkspaceNav from "../Components/WorkspaceNav";

export default function Home() {
  const { user } = useSession();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [mode, setMode] = useState("");
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    let active = true;
    api
      .jobs()
      .then((data) => {
        if (active) setJobs(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  const normalize = (value) =>
    (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  const filtered = jobs.filter(
    (job) =>
      normalize(`${job.titulo} ${job.nombre_empresa}`).includes(
        normalize(search),
      ) &&
      normalize(job.ubicacion).includes(normalize(location)) &&
      (!mode || job.modalidad === mode),
  );
  if (user?.tipo === "empresa") return <Navigate to="/hub-empresa" replace />;
  return (
    <>
      {user && (
        <div className="contenedor dashboard">
          <WorkspaceNav />
          <h1>Explora las ofertas</h1>
        </div>
      )}
      {!user && (
        <section className="hero contenedor">
          <div className="hero-copy">
            <h1>Empleo para recién egresados</h1>
            <div className="hero-links">
              <Link className="boton boton-primario" to="/registro">
                Crea tu perfil gratis <FiArrowRight />
              </Link>
              <a href="#ofertas">Explorar ofertas ↓</a>
            </div>
          </div>
        </section>
      )}
      <section id="ofertas" className="contenedor jobs-section">
        <div className="section-heading">
          <div>
            <h2>Ofertas de empleo</h2>
          </div>
          <span className="results-count" role="status" aria-atomic="true">
            {loading
              ? "Cargando…"
              : `${filtered.length} ${
                  filtered.length === 1 ? "oferta" : "ofertas"
                }`}
          </span>
        </div>
        <form
          className="search-bar"
          onSubmit={(e) => {
            e.preventDefault();
            document
              .getElementById("resultados")
              .scrollIntoView({ behavior: "auto" });
          }}
        >
          <label>
            <FiSearch />
            <span className="search-label">Cargo o empresa</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cargo o empresa"
            />
          </label>
          <label>
            <FiMapPin />
            <span className="search-label">Ciudad o región</span>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Ciudad o región"
            />
          </label>
          <label>
            <span className="search-label">Modalidad</span>
            <select value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="">Todas las modalidades</option>
              <option value="presencial">Presencial</option>
              <option value="remoto">Remoto</option>
              <option value="hibrido">Híbrido</option>
            </select>
          </label>
          <button className="boton boton-primario">
            Buscar <FiSearch />
          </button>
        </form>
        <div id="resultados" aria-live="polite">
          {loading && <p className="empty-state">Buscando oportunidades…</p>}
          {error && (
            <p className="mensaje-error" role="alert">
              {error}
            </p>
          )}
          {!loading && !error && !filtered.length && (
            <div className="empty-state">
              <FiBriefcase />
              <h3>
                {jobs.length
                  ? "No encontramos coincidencias"
                  : "Las próximas oportunidades empiezan aquí"}
              </h3>
              <p>
                {jobs.length
                  ? "Prueba con otro cargo, ciudad o modalidad."
                  : "Todavía no hay ofertas publicadas. Mientras tanto, prepara tu perfil profesional."}
              </p>
              <Link
                to={
                  user
                    ? user.tipo === "empresa"
                      ? "/ofertas-empresa"
                      : "/perfil-egresado"
                    : "/registro"
                }
              >
                {user ? "Ir a mi espacio" : "Crear una cuenta"} <FiArrowRight />
              </Link>
            </div>
          )}
        </div>
        <div className="job-grid">
          {filtered.map((job) => (
            <article key={job.id} className="job-card">
              <div className="job-card-top">
                <span className="company-icon">
                  {job.nombre_empresa.slice(0, 2).toUpperCase()}
                </span>
                <span className="job-mode">
                  {job.modalidad === "hibrido"
                    ? "Híbrido"
                    : job.modalidad || "Por definir"}
                </span>
              </div>
              <p className="muted">{job.nombre_empresa}</p>
              <h3>{job.titulo}</h3>
              <p className="job-location">
                <FiMapPin />
                {job.ubicacion || "Ubicación por definir"}
              </p>
              <p className="job-excerpt">{job.descripcion}</p>
              <button
                className="job-detail"
                onClick={() => setSelected(selected === job.id ? null : job.id)}
                aria-expanded={selected === job.id}
                aria-controls={`job-detail-${job.id}`}
                aria-label={`${
                  selected === job.id ? "Cerrar detalle" : "Ver oportunidad"
                }: ${job.titulo}`}
              >
                {selected === job.id ? "Cerrar detalle" : "Ver oportunidad"}{" "}
                <FiArrowUpRight />
              </button>
              {selected === job.id && (
                <div className="job-expanded" id={`job-detail-${job.id}`}>
                  <p>{job.descripcion}</p>
                  <JobFacts job={job} />
                  <strong>Requisitos</strong>
                  <p>
                    {job.requisitos ||
                      "La empresa no ha indicado requisitos adicionales."}
                  </p>
                  {user?.tipo === "empresa" ? (
                    <p className="muted">
                      Las postulaciones están disponibles para cuentas de
                      egresados.
                    </p>
                  ) : (
                    <Link
                      className="boton boton-primario"
                      to={
                        user ? `/ofertas/${job.id}/postular` : "/iniciar-sesion"
                      }
                    >
                      {user
                        ? "Postular a esta oferta"
                        : "Inicia sesión para postular"}
                    </Link>
                  )}
                </div>
              )}
            </article>
          ))}
        </div>
      </section>
      {!user && (
        <>
          <section className="contenedor company-cta">
            <div>
              <h2>Publica ofertas de empleo</h2>
            </div>
            <Link className="boton boton-primario" to="/registro/empresa">
              Registra tu empresa <FiArrowRight />
            </Link>
          </section>
        </>
      )}
    </>
  );
}
