import PropTypes from "prop-types";
import {
  FiGithub,
  FiExternalLink,
  FiMail,
  FiPhone,
  FiMapPin,
  FiAward,
} from "react-icons/fi";
import { emptyPortfolio, growth } from "../portfolio";
import GrowthTree from "./GrowthTree";
import { Asset } from "./Media";

function External({ url, children }) {
  return url ? (
    <a className="text-link" href={url} target="_blank" rel="noreferrer">
      {children}
      <FiExternalLink />
    </a>
  ) : null;
}
External.propTypes = { url: PropTypes.string, children: PropTypes.node };

export default function PortfolioView({ profile, editing = false }) {
  const p = { ...emptyPortfolio, ...profile.portfolio };
  const { percent } = growth(profile);
  return (
    <div className={`portfolio theme-${p.tema}`}>
      <section className="portfolio-cover">
        <div className="portfolio-avatar">
          {p.foto_id ? (
            <Asset id={p.foto_id} alt={`Foto de ${profile.nombre}`} />
          ) : profile.foto_url ? (
            <img src={profile.foto_url} alt={`Foto de ${profile.nombre}`} />
          ) : (
            <span>
              {profile.nombre?.[0]}
              {profile.apellido?.[0]}
            </span>
          )}
        </div>
        <div className="portfolio-intro">
          <h1>
            {profile.nombre} <em>{profile.apellido}</em>
          </h1>
          <p className="portfolio-title">
            {p.titular || profile.carrera || ""}
          </p>
          <div className="portfolio-meta">
            {p.ubicacion && (
              <span>
                <FiMapPin />
                {p.ubicacion}
              </span>
            )}
            <span className="availability">
              <i />
              {p.disponibilidad}
            </span>
          </div>
        </div>
      </section>
      <div className="portfolio-columns">
        <div>
          <section className="story-card">
            <h2>Sobre mí</h2>
            <p className="personal-story">
              {profile.presentacion || "Sin presentación."}
            </p>
            {(p.video_id || p.video_url) && (
              <div className="intro-video">
                {p.video_id ? (
                  <Asset
                    id={p.video_id}
                    type="video"
                    alt="Video de presentación"
                  />
                ) : (
                  <External url={p.video_url}>
                    Ver mi presentación de 1 minuto
                  </External>
                )}
              </div>
            )}
          </section>
          <section className="projects-section">
            <div className="section-heading">
              <div>
                <h2>Proyectos</h2>
              </div>
            </div>
            {!p.proyectos.length ? (
              <div className="garden-empty">
                {editing
                  ? "Añade proyectos desde el editor."
                  : "Sin proyectos."}
              </div>
            ) : (
              <div className="portfolio-projects">
                {p.proyectos.map((project, i) => (
                  <article className="project-story" key={i}>
                    <div className="project-art">
                      <span>{String(i + 1).padStart(2, "0")}</span>
                      <b>{project.tipo === "Académico" ? "↗" : "✳"}</b>
                      <small>{project.tipo}</small>
                    </div>
                    <div className="project-body">
                      <h3>{project.titulo}</h3>
                      <p>{project.descripcion}</p>
                      <div className="skill-chips">
                        {project.tecnologias.map((t, k) => (
                          <span key={k}>{t}</span>
                        ))}
                      </div>
                      {project.video_id && (
                        <Asset
                          id={project.video_id}
                          type="video"
                          alt={`Demo de ${project.titulo}`}
                        />
                      )}
                      <div className="project-links">
                        <External url={project.github_url}>
                          <FiGithub />
                          Código
                        </External>
                        <External url={project.proyecto_url}>
                          Ver proyecto
                        </External>
                        <External url={project.video_url}>
                          Ver demo en video
                        </External>
                      </div>
                      {project.qr_id && (
                        <figure className="project-qr">
                          <Asset
                            id={project.qr_id}
                            alt={`QR del proyecto ${project.titulo}`}
                          />
                          <figcaption>Escanea y explora el proyecto</figcaption>
                        </figure>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
          <section className="certificates-section">
            <h2>Certificaciones</h2>
            {!p.certificaciones.length ? (
              <p className="garden-empty">
                Aquí aparecerán las certificaciones que añadas.
              </p>
            ) : (
              p.certificaciones.map((item, i) => (
                <article className="certificate" key={i}>
                  <FiAward />
                  <div>
                    <h3>{item.nombre}</h3>
                    <p>{item.entidad}</p>
                    <div className="project-links">
                      <External url={item.url}>Ver credencial</External>
                      {item.archivo_id && (
                        <Asset
                          id={item.archivo_id}
                          type="document"
                          label="Abrir certificado"
                        />
                      )}
                    </div>
                  </div>
                </article>
              ))
            )}
          </section>
        </div>
        <aside className="portfolio-aside">
          <section className="tree-card">
            <GrowthTree percent={percent} />
            <h3>Desarrollo profesional</h3>

            <div className="tree-counts">
              <span>
                <strong>{p.proyectos.length}</strong>proyectos
              </span>
              <span>
                <strong>{p.habilidades.length}</strong>habilidades
              </span>
              <span>
                <strong>{p.certificaciones.length}</strong>certificados
              </span>
            </div>
          </section>
          <section className="skills-card">
            <h2>Habilidades</h2>
            {!p.habilidades.length ? (
              <p>Aún no hay habilidades añadidas.</p>
            ) : (
              p.habilidades.map((skill, i) => (
                <div className="skill-row" key={i}>
                  <div>
                    <strong>{skill.nombre}</strong>
                    <small>{skill.nivel}</small>
                  </div>
                  <div className="skill-track">
                    <span
                      style={{
                        width:
                          skill.nivel === "Avanzado"
                            ? "90%"
                            : skill.nivel === "Intermedio"
                            ? "60%"
                            : "30%",
                      }}
                    />
                  </div>
                </div>
              ))
            )}
            {p.habilidades.length > 0 && (
              <small>Niveles declarados por la persona.</small>
            )}
          </section>
          {profile.carrera && (
            <section className="education-card">
              <h3>{profile.carrera}</h3>
              {profile.anio_egreso && <p>Egreso · {profile.anio_egreso}</p>}
            </section>
          )}
          <section className="contact-card">
            <h2>Contacto</h2>
            {(editing || p.mostrar_email) && p.contacto_email && (
              <a href={`mailto:${p.contacto_email}`}>
                <FiMail />
                {p.contacto_email}
              </a>
            )}
            {(editing || p.mostrar_telefono) && p.contacto_telefono && (
              <a href={`tel:${p.contacto_telefono.replace(/[^+\d]/g, "")}`}>
                <FiPhone />
                {p.contacto_telefono}
              </a>
            )}
            <External url={p.github_url}>
              <FiGithub />
              GitHub
            </External>
            <External url={profile.linkedin_url}>LinkedIn</External>
            <p>Disponibilidad: {p.disponibilidad}</p>
          </section>
        </aside>
      </div>
      <div className="portfolio-signoff">
        BranchIT <span>❧</span> <small>Un portafolio hecho en BranchIt</small>
      </div>
    </div>
  );
}
PortfolioView.propTypes = {
  profile: PropTypes.object.isRequired,
  editing: PropTypes.bool,
};
