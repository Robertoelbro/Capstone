import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FiArrowUpRight,
  FiSearch,
  FiMapPin,
  FiArrowRight,
  FiBookOpen,
  FiCode,
  FiUser,
} from "react-icons/fi";
import { api } from "../api";
import { useSession } from "../session";
import { growth, normalize } from "../portfolio";
import GraduateLayout from "../Components/GraduateLayout";

export default function GraduateHub() {
  const { user } = useSession();
  const [data, setData] = useState(null),
    [error, setError] = useState("");
  const [scope, setScope] = useState("afin"),
    [search, setSearch] = useState(""),
    [category, setCategory] = useState(""),
    [mode, setMode] = useState(""),
    [city, setCity] = useState(""),
    [limit, setLimit] = useState(9);
  useEffect(() => {
    let active = true;
    Promise.all([
      api.obtenerPerfilEgresado(user.id),
      api.recommendations(user.id),
      api.myApplications(),
    ])
      .then(([profile, jobs, applications]) => {
        if (active) setData({ profile, jobs, applications });
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [user.id]);
  function filter(setter, value) {
    setter(value);
    setLimit(9);
  }
  if (!data)
    return (
      <GraduateLayout>
        <p role={error ? "alert" : "status"}>
          {error || "Buscando oportunidades para ti…"}
        </p>
      </GraduateLayout>
    );
  const { profile, jobs, applications } = data;
  const area = jobs.find((j) => j.area_carrera)?.area_carrera;
  const matching = jobs.filter((j) => j.afin);
  const filtered = jobs.filter(
    (j) =>
      (scope !== "afin" || !area || j.afin) &&
      (!category || j.categoria === category) &&
      (!mode || j.modalidad === mode) &&
      normalize(`${j.titulo} ${j.nombre_empresa} ${j.categoria}`).includes(
        normalize(search),
      ) &&
      normalize(j.ubicacion).includes(normalize(city)),
  );
  const { steps, percent } = growth(profile);
  const projects = profile.portfolio?.proyectos || [];
  return (
    <GraduateLayout profile={profile}>
      <div className="hub-heading">
        <div>
          <h1>
            Hola, {profile.nombre}
            <span className="wave-leaf">❧</span>
          </h1>
        </div>
        <Link
          className="round-link"
          to="/perfil-egresado"
          aria-label="Ver mi portafolio"
        >
          <FiUser />
        </Link>
      </div>
      <div className="hub-columns">
        <div className="hub-main">
          <section className="recommendation-banner">
            <div>
              <span className="pill">PARA TI · SEGÚN TU CARRERA</span>
              <h2>Ofertas afines a mi carrera</h2>
              <p>
                {area
                  ? `Encontramos ${
                      matching.length
                    } ofertas del área de ${area.toLowerCase()}.`
                  : "Añade tu carrera al perfil para encontrar oportunidades afines."}
              </p>
              <small>
                Coincidencias por carrera y categoría. Revisa siempre los
                requisitos de cada oferta.
              </small>
              <a href="#hub-ofertas">
                Ver ofertas <FiArrowRight />
              </a>
            </div>
            <div className="recommendation-paper">
              <span className="paper-pin" />
              {(matching.length ? matching : jobs).slice(0, 3).map((j, i) => (
                <Link to={`/ofertas/${j.id}/postular`} key={j.id}>
                  <span>0{i + 1}</span>
                  <div>
                    <strong>{j.titulo}</strong>
                    <small>{j.nombre_empresa}</small>
                  </div>
                  <FiArrowUpRight />
                </Link>
              ))}
              {!jobs.length && <p>Aún no hay ofertas publicadas.</p>}
            </div>
          </section>
          <section className="hub-projects">
            <div className="section-heading">
              <div>
                <h2>Mis proyectos</h2>
              </div>
              <Link to="/perfil-egresado">Mi portafolio ↗</Link>
            </div>
            <div className="mini-project-grid">
              {projects.slice(0, 2).map((p, i) => (
                <Link className="mini-project" key={i} to="/perfil-egresado">
                  <div className="mini-art">
                    <FiCode />
                    <span>0{i + 1}</span>
                  </div>
                  <div>
                    <small>{p.tipo}</small>
                    <h3>{p.titulo}</h3>
                    <p>{p.descripcion}</p>
                    <div className="skill-chips">
                      {p.tecnologias.slice(0, 3).map((t, k) => (
                        <span key={k}>{t}</span>
                      ))}
                    </div>
                  </div>
                </Link>
              ))}
              {projects.length < 2 && (
                <Link className="project-invitation" to="/perfil-egresado">
                  <span>＋</span>
                  <strong>Añadir proyecto</strong>
                </Link>
              )}
            </div>
          </section>
          <section className="hub-jobs" id="hub-ofertas">
            <div className="section-heading">
              <div>
                <h2>Ofertas de empleo</h2>
              </div>
              <span>{filtered.length} ofertas</span>
            </div>
            <div className="view-switch">
              <button
                aria-pressed={scope === "afin"}
                onClick={() => filter(setScope, "afin")}
              >
                Afines a mi carrera
              </button>
              <button
                aria-pressed={scope === "all"}
                onClick={() => filter(setScope, "all")}
              >
                Todas las oportunidades
              </button>
            </div>
            {scope === "afin" && !area && (
              <p className="filter-note">
                Todavía no identificamos tu área. Mostramos todas las ofertas;
                puedes elegir una categoría o actualizar tu carrera.
              </p>
            )}
            <div className="hub-filters">
              <label>
                <FiSearch />
                <input
                  aria-label="Cargo, empresa o categoría"
                  placeholder="Cargo, empresa o categoría"
                  value={search}
                  onChange={(e) => filter(setSearch, e.target.value)}
                />
              </label>
              <label>
                <FiMapPin />
                <input
                  aria-label="Ciudad o región"
                  placeholder="Ciudad o región"
                  value={city}
                  onChange={(e) => filter(setCity, e.target.value)}
                />
              </label>
              <select
                aria-label="Categoría"
                value={category}
                onChange={(e) => filter(setCategory, e.target.value)}
              >
                <option value="">Todas las categorías</option>
                {[...new Set(jobs.map((j) => j.categoria))].sort().map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
              <select
                aria-label="Modalidad"
                value={mode}
                onChange={(e) => filter(setMode, e.target.value)}
              >
                <option value="">Cualquier modalidad</option>
                {["Presencial", "Híbrido", "Remoto"].map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
            <div className="garden-job-grid">
              {filtered.slice(0, limit).map((j) => (
                <article className="garden-job" key={j.id}>
                  <div className="job-top">
                    <span className="job-initial">
                      {j.nombre_empresa.replace("DEMO · ", "").slice(0, 2)}
                    </span>
                    <span>{j.modalidad || "A convenir"}</span>
                  </div>
                  <small>{j.nombre_empresa}</small>
                  <h3>{j.titulo}</h3>
                  <p>
                    <FiMapPin />
                    {j.ubicacion || "Ubicación por definir"}
                  </p>
                  <span className="category-tag">{j.categoria}</span>
                  {j.afin && <p className="match-reason">❧ {j.motivo}</p>}
                  <Link to={`/ofertas/${j.id}/postular`}>
                    Ver oportunidad <FiArrowUpRight />
                  </Link>
                </article>
              ))}
            </div>
            {!filtered.length && (
              <div className="garden-empty">
                <h3>No hay ofertas con estos filtros.</h3>
                <p>Puedes ampliar tu búsqueda y explorar otras áreas.</p>
                <button
                  type="button"
                  onClick={() => {
                    setScope("all");
                    setCategory("");
                    setMode("");
                    setSearch("");
                    setCity("");
                  }}
                >
                  Ver todas las oportunidades
                </button>
              </div>
            )}
            {limit < filtered.length && (
              <button
                className="load-more"
                onClick={() => setLimit((n) => n + 9)}
              >
                Mostrar más ofertas
              </button>
            )}
          </section>
        </div>
        <aside className="hub-aside">
          <section className="next-step-card">
            <FiBookOpen />
            <h2>Completar perfil</h2>
            <strong>{percent}% de tu perfil completo</strong>
            <progress
              value={percent}
              max="100"
              aria-label="Progreso del perfil"
            />
            <div>
              {steps
                .filter(([, done]) => !done)
                .slice(0, 3)
                .map(([name]) => (
                  <Link key={name} to="/perfil-egresado">
                    <span>＋</span>
                    {name}
                    <FiArrowUpRight />
                  </Link>
                ))}
            </div>
            {percent === 100 && (
              <p>Tu perfil está completo. Mantén tus proyectos al día.</p>
            )}
          </section>
          <section className="recent-card">
            <h2>Mis postulaciones</h2>
            {applications.length ? (
              applications.slice(0, 4).map((a) => (
                <Link key={a.id} to="/mis-postulaciones">
                  <span className="activity-seed">↗</span>
                  <div>
                    <strong>{a.titulo}</strong>
                    <small>Postulación enviada · {a.nombre_empresa}</small>
                  </div>
                </Link>
              ))
            ) : (
              <p>Aún no has postulado.</p>
            )}
            <Link className="text-link" to="/mis-postulaciones">
              Ver mis postulaciones ↗
            </Link>
          </section>
        </aside>
      </div>
    </GraduateLayout>
  );
}
