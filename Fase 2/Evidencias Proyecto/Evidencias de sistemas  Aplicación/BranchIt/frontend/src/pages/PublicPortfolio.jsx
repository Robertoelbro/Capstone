import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import PortfolioView from "../Components/PortfolioView";

export default function PublicPortfolio() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setError("");
    setProfile(null);
    api
      .publicPortfolio(id)
      .then((p) => {
        if (active) setProfile(p);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [id]);
  return (
    <div className="public-portfolio">
      {error ? (
        <div className="garden-empty">
          <h1>Portafolio no disponible</h1>
          <p>{error}</p>
          <Link to="/">Volver a BranchIt</Link>
        </div>
      ) : profile ? (
        <PortfolioView profile={profile} />
      ) : (
        <p role="status">Cargando portafolio…</p>
      )}
    </div>
  );
}
