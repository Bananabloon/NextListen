
const LoginButton = () => {
  const handleLogin = () => {
    window.location.href = "https://86d5-92-63-39-59.ngrok-free.app/api/auth/spotify/login/";
  };

  return (
    <button
      onClick={handleLogin}
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        backgroundColor: '#1DB954',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer'
      }}
    >
      Zaloguj się przez Spotify
    </button>
  );
};

export default LoginButton;
