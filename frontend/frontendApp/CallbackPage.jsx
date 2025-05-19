import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function CallbackPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    if (!code) return;

    fetch(`http://localhost:8000/auth/spotify/callback/?code=${code}`)
      .then(res => res.json())
      .then(data => {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        // Możesz też zapisać user info np. w context, redux albo localStorage
        navigate("/dashboard");
      })
      .catch(() => {
        // obsłuż błąd, np. przekieruj do logowania
      });
  }, []);

  return <p>Logging in...</p>;
}

export default CallbackPage;
