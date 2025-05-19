import { useEffect, useState } from "react";

const HomePage = () => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const access = localStorage.getItem("accessToken");
    setToken(access);
  }, []);

  return (
    <div>
      <h1>Witaj w aplikacji!</h1>
      {token ? (
        <p>Masz token: <code>{token.slice(0, 20)}...</code></p>
      ) : (
        <p>Nie jesteś zalogowany.</p>
      )}
    </div>
  );
};

export default HomePage;
