import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

// 🔑 CONFIGURACIÓN SEGURA DESDE VARIABLES DE ENTORNO
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000/api/v1";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export default function App() {
  const [session, setSession] = useState<any>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loadingAuth, setLoadingAuth] = useState(false);

  // Estado del formulario
  const [formData, setFormData] = useState({ cliente_id_interno: "", monto_deuda: "", dias_mora: "" });
  const [generando, setGenerando] = useState(false);
  const [resultado, setResultado] = useState<{ mensaje: string; modo: string; cliente: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Manejo de sesión de Supabase
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => setSession(session));
    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingAuth(true);
    setError(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setError(error.message);
    setLoadingAuth(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setResultado(null);
    setFormData({ cliente_id_interno: "", monto_deuda: "", dias_mora: "" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerando(true);
    setError(null);
    setResultado(null);

    try {
      if (!session?.access_token) throw new Error("Sesión no activa. Inicia sesión nuevamente.");

      const payload = {
        cliente_id_interno: formData.cliente_id_interno,
        monto_deuda: parseFloat(formData.monto_deuda),
        dias_mora: parseInt(formData.dias_mora)
      };

      const res = await fetch(`${BACKEND_URL}/generar-mensaje`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${session.access_token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || `Error HTTP: ${res.status}`);
      }

      const data = await res.json();
      setResultado({
        mensaje: data.mensaje_generado,
        modo: data.modo, 
        cliente: data.cliente_anonimo
      });
    } catch (err: any) {
      setError(err.message || "Error desconocido al conectar con el backend.");
    } finally {
      setGenerando(false);
    }
  };

  // VISTA: LOGIN
  if (!session) {
    return (
      <div style={{ maxWidth: "400px", margin: "50px auto", padding: "20px", fontFamily: "system-ui, sans-serif", textAlign: "center" }}>
        <h2 style={{ color: "#1e293b" }}>🔐 Acceso AI-Cobranza</h2>
        {error && <p style={{ color: "#ef4444", background: "#fef2f2", padding: "10px", borderRadius: "6px" }}>{error}</p>}
        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "20px" }}>
          <input type="email" placeholder="Email (ej: admin@prueba-cobranza.com)" value={email} onChange={e => setEmail(e.target.value)} required style={{ padding: "12px", border: "1px solid #cbd5e1", borderRadius: "6px" }} />
          <input type="password" placeholder="Contraseña" value={password} onChange={e => setPassword(e.target.value)} required style={{ padding: "12px", border: "1px solid #cbd5e1", borderRadius: "6px" }} />
          <button type="submit" disabled={loadingAuth} style={{ padding: "12px", background: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", fontWeight: "bold", cursor: "pointer", opacity: loadingAuth ? 0.7 : 1 }}>
            {loadingAuth ? "Ingresando..." : "Iniciar Sesión"}
          </button>
        </form>
      </div>
    );
  }

  // VISTA: DASHBOARD DE COBRANZA
  return (
    <div style={{ maxWidth: "700px", margin: "30px auto", padding: "20px", fontFamily: "system-ui, sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", paddingBottom: "16px", borderBottom: "1px solid #e2e8f0" }}>
        <h1 style={{ fontSize: "1.5rem", color: "#0f172a", margin: 0 }}>🤖 AI-Cobranza MVP</h1>
        <button onClick={handleLogout} style={{ padding: "8px 16px", background: "#fee2e2", color: "#991b1b", border: "1px solid #fecaca", borderRadius: "6px", cursor: "pointer", fontWeight: "500" }}>Cerrar Sesión</button>
      </header>

      <form onSubmit={handleSubmit} style={{ background: "#f8fafc", padding: "24px", borderRadius: "8px", marginBottom: "24px", border: "1px solid #e2e8f0" }}>
        <h3 style={{ marginTop: 0, color: "#334155" }}>Generar Mensaje de Cobranza</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "16px" }}>
          <input placeholder="ID Cliente Interno" value={formData.cliente_id_interno} onChange={e => setFormData({...formData, cliente_id_interno: e.target.value})} required style={{ padding: "10px", border: "1px solid #cbd5e1", borderRadius: "6px" }} />
          <input type="number" step="0.01" placeholder="Monto Deuda ($)" value={formData.monto_deuda} onChange={e => setFormData({...formData, monto_deuda: e.target.value})} required style={{ padding: "10px", border: "1px solid #cbd5e1", borderRadius: "6px" }} />
          <input type="number" placeholder="Días Mora" value={formData.dias_mora} onChange={e => setFormData({...formData, dias_mora: e.target.value})} required style={{ padding: "10px", border: "1px solid #cbd5e1", borderRadius: "6px" }} />
        </div>
        <button type="submit" disabled={generando} style={{ width: "100%", padding: "12px", background: generando ? "#94a3b8" : "#16a34a", color: "#fff", border: "none", borderRadius: "6px", cursor: generando ? "not-allowed" : "pointer", fontWeight: "bold", fontSize: "1rem" }}>
          {generando ? "⏳ Procesando con IA..." : "✨ Generar Mensaje"}
        </button>
      </form>

      {error && <p style={{ color: "#991b1b", background: "#fef2f2", padding: "12px", borderRadius: "6px", textAlign: "center" }}>❌ {error}</p>}

      {resultado && (
        <div style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "20px", background: "#ffffff", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <strong style={{ color: "#475569" }}>Destinatario: {resultado.cliente}</strong>
            {resultado.modo === "cache_hit" ? (
              <span style={{ background: "#dcfce7", color: "#166534", padding: "6px 12px", borderRadius: "20px", fontSize: "0.85rem", fontWeight: "bold", display: "flex", alignItems: "center", gap: "6px" }}>
                ⚡ CACHÉ (0 Tokens IA)
              </span>
            ) : (
              <span style={{ background: "#fef3c7", color: "#92400e", padding: "6px 12px", borderRadius: "20px", fontSize: "0.85rem", fontWeight: "bold", display: "flex", alignItems: "center", gap: "6px" }}>
                🤖 IA (Generado en tiempo real)
              </span>
            )}
          </div>
          <p style={{ fontSize: "1.1rem", lineHeight: "1.6", color: "#0f172a", margin: 0, whiteSpace: "pre-wrap" }}>{resultado.mensaje}</p>
        </div>
      )}
    </div>
  );
}