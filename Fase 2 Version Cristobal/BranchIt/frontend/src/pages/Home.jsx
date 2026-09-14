import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  return (
    <div className="contenedor home">
      <section className="home-hero">
        <svg
          className="home-hero__rama"
          viewBox="0 0 200 200"
          role="presentation"
          aria-hidden="true"
        >
          <path
            d="M100 190 V110 M100 110 C60 110 60 70 40 40 M100 110 C140 110 140 70 160 40 M100 150 C70 150 70 120 55 100 M100 150 C130 150 130 120 145 100"
            fill="none"
            stroke="var(--color-primary)"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx="40" cy="40" r="6" fill="var(--color-accent)" />
          <circle cx="160" cy="40" r="6" fill="var(--color-accent)" />
          <circle cx="55" cy="100" r="5" fill="var(--color-primary-light)" />
          <circle cx="145" cy="100" r="5" fill="var(--color-primary-light)" />
        </svg>

        <div>
          <h1>Cada egresado tiene varios caminos por delante.</h1>
          <p className="home-hero__bajada">
            BranchIt conecta a egresados de DuocUC con empresas que publican
            ofertas de empleo reales, en un solo lugar.
          </p>
          <div className="home-hero__acciones">
            <Link to="/registro/egresado" className="boton boton-primario">
              Soy egresado
            </Link>
            <Link to="/registro/empresa" className="boton boton-secundario">
              Soy empresa
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
