import { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../services/api";
import { API_BASE } from "../config";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem("access_token")
  );
  const [refreshToken, setRefreshToken] = useState(() =>
    localStorage.getItem("refresh_token")
  );
  const [loading, setLoading] = useState(true);

  const isAuthenticated = Boolean(accessToken && user);

  const storeAuth = useCallback((data) => {
    const { access_token, refresh_token, user: userData } = data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("user", JSON.stringify(userData));
    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    setUser(userData);
  }, []);

  const clearAuth = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  const login = useCallback(
    async (username, password) => {
      const response = await api.post("/auth/login", { username, password });
      storeAuth(response.data);
      return response.data;
    },
    [storeAuth]
  );

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  // On mount: if refresh_token exists, try to validate/refresh it
  useEffect(() => {
    async function initAuth() {
      const storedRefresh = localStorage.getItem("refresh_token");
      if (!storedRefresh) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.post("/auth/refresh", {
          refresh_token: storedRefresh,
        });
        storeAuth(response.data);
      } catch {
        // Refresh token is invalid or expired — clear everything
        clearAuth();
      } finally {
        setLoading(false);
      }
    }

    initAuth();
  }, [storeAuth, clearAuth]);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, login, logout, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
