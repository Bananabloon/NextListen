const ngrokUrl = import.meta.env.VITE_NGROK_URL;
const LoginButton = () => {
    const handleLogin = () => {
        window.location.href = `${ngrokUrl}/api/auth/spotify/login/`;
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
                cursor: 'pointer',
            }}
        >
            Zaloguj się przez Spotify
        </button>
    );
};

export default LoginButton;
