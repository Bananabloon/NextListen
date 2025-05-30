import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./HomePage.module.css";
import { API_URL } from "../../config/url.config";
import { useNavigate } from "react-router-dom";

const HomePage = (): React.JSX.Element => {
    const navigate = useNavigate();

    return (
        <Stack className={classes.container}>
            <Button
                variant="spotify"
                size="lg"
                onClick={() => navigate("/login")}
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
