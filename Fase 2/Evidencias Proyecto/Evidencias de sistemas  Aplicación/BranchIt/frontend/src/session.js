import { createContext, useContext } from "react";

export const SessionContext = createContext(null);
export const useSession = () => useContext(SessionContext);
export const panelPath = (user) =>
  user?.tipo === "empresa" ? "/hub-empresa" : "/hub-egresado";
