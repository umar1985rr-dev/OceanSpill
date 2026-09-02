import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconDroplet } from "../components/ui/icons";
import api from "../services/api";

export default function Register() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  function update(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/register", {
        username: form.username,
        email: form.email,
        password: form.password,
        full_name: form.full_name || undefined,
      });
      // Registration successful — log in automatically
      const loginRes = await api.post("/auth/login", {
        username: form.username,
        password: form.password,
      });
      const { access_token, refresh_token, user } = loginRes.data;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      localStorage.setItem("user", JSON.stringify(user));
      navigate("/", { replace: true });
    } catch (err) {
      const detail =
        err.response?.data?.detail || "Registration failed";
      setError(typeof detail === "string" ? detail : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-ocean-950">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-auto">
        {/* Branding */}
        <div className="flex flex-col items-center mb-6">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-primary/10 mb-4">
            <IconDroplet className="text-primary" size={28} />
          </div>
          <h1 className="text-2xl font-bold text-ocean-950">Create Account</h1>
          <p className="text-sm text-muted">Join OceanSpill</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            placeholder="Full name"
            value={form.full_name}
            onChange={update("full_name")}
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition bg-slate-50"
          />
          <input
            type="text"
            placeholder="Username *"
            value={form.username}
            onChange={update("username")}
            required
            autoComplete="username"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition bg-slate-50"
          />
          <input
            type="email"
            placeholder="Email *"
            value={form.email}
            onChange={update("email")}
            required
            autoComplete="email"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition bg-slate-50"
          />
          <input
            type="password"
            placeholder="Password *"
            value={form.password}
            onChange={update("password")}
            required
            autoComplete="new-password"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition bg-slate-50"
          />
          <input
            type="password"
            placeholder="Confirm password *"
            value={form.confirmPassword}
            onChange={update("confirmPassword")}
            required
            autoComplete="new-password"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition bg-slate-50"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-primary-hover text-white font-semibold py-3 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin size-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating account...
              </span>
            ) : (
              "Create Account"
            )}
          </button>

          {error && <p className="text-danger text-sm text-center mt-2">{error}</p>}
        </form>

        <p className="text-center text-sm text-muted mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-primary font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
