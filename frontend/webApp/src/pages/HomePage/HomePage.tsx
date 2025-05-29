import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./HomePage.module.css";
import { API_URL } from "../../config/url.config";

const HomePage = (): React.JSX.Element => {
    const navigateToLogin = () => (window.location.href = `${API_URL}/auth/spotify/login/`);

    return (
        <Stack className={classes.container}>
            <Button
                variant="spotify"
                size="lg"
                onClick={navigateToLogin}
            >
                Log in with Spotify{" "}
                <img
                    src="icons/spotify/logo_black.svg"
                    style={{ height: 32 }}
                />
            </Button>
        </Stack>
    );
};

export default HomePage;
