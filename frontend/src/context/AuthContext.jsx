import { createContext, useContext, useEffect, useState } from "react";
import { api, setToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("ep_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("auth/me/")
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const data = await api.post("auth/login/", { username, password }, { auth: false });
    setToken(data.token);
    setUser(data.user);
    return data.user;
  }

  async function register(username, password, role) {
    const data = await api.post("auth/register/", { username, password, role }, { auth: false });
    setToken(data.token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
