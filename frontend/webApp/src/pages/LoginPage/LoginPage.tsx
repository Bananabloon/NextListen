import { API_URL } from "../../config/url.config";

const LoginPage = (): React.JSX.Element => {
    window.location.href = `${API_URL}/auth/spotify/login/`;
    return <></>;
};

export default LoginPage;
