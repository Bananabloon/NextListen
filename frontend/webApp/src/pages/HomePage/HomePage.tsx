import { IconCube3dSphere } from "@tabler/icons-react";
import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./HomePage.module.css";
import { useNavigate } from "react-router-dom";
import { RingLoader } from "react-spinners";
const HomePage = (): React.JSX.Element => {
    const navigate = useNavigate();

    return (
        <>
            {/* <IconCube3dSphere
                size={1024}
                stroke={0.05}
                className={classes.backgroundIcon}
            /> */}
            <h1 className={classes.title}>NextListen</h1>
            <Stack className={classes.container}>
                <h1 className={classes.introText}>
                    Next Level music recommendations
                    <br />
                    with You in mind.
                </h1>
                <h2 className={classes.descriptionText}>
                    Take Your music listening experience to the next level with <br />
                    personalized recommendations guided by Your feedback
                </h2>
                <Button
                    className={classes.loginButton}
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
                <RingLoader
                    size="500"
                    color="#FFFFFF"
                    speedMultiplier={0.5}
                    cssOverride={{
                        opacity: 0.2,
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%,-50%)",
                        zIndex: "-1",
                    }}
                />
            </Stack>
        </>
    );
};

export default HomePage;
