import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { api, clearToken, setToken, getToken } from "./api";
import { SessionContext } from "./session";

export default function SessionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));
  useEffect(() => {
    let active = true;
    const expired = () => {
      clearToken();
      setUser(null);
    };
    window.addEventListener("session-expired", expired);
    if (getToken())
      api
        .me()
        .then((data) => {
          if (active) setUser(data);
        })
        .catch(() => {
          if (active) expired();
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    return () => {
      active = false;
      window.removeEventListener("session-expired", expired);
    };
  }, []);
  async function login(data) {
    const result = await api.login(data);
    setToken(result.access_token);
    setUser(result.user);
    return result.user;
  }
  async function logout() {
    await api.logout();
    clearToken();
    setUser(null);
  }
  return (
    <SessionContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </SessionContext.Provider>
  );
}
SessionProvider.propTypes = { children: PropTypes.node.isRequired };
