import { IconCube3dSphere } from "@tabler/icons-react";
import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./HomePage.module.css";
import { useNavigate } from "react-router-dom";
import { RingLoader } from "react-spinners";
import Group from "../../components/atoms/Group/Group";
import IconButton from "../../components/atoms/IconButton/IconButton";
const HomePage = (): React.JSX.Element => {
    const navigate = useNavigate();

    return (
        <>
            {/* <IconCube3dSphere
                size={1024}
                stroke={0.05}
                className={classes.backgroundIcon}
            /> */}
            <Group style={{ gap: 0, justifyContent: "center" }}>
                <img
                    src="icons\nextlisten\nextlisten.svg"
                    width={32}
                    style={{ marginLeft: "var(--spacing-xxxl)" }}
                />
                <h1 className={classes.title}>NextListen</h1>
            </Group>
            <Group style={{ alignItems: "center", justifyContent: "space-around" }}>
                <div className={classes.sideTextBlock}>
                    <p className={classes.titleText}>How does it work?</p>
                    <p className={classes.smallerText}>
                        Our system lets you generate song queues based on different factors and listen to the music directly through the
                        app!
                    </p>
                </div>
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
                <div className={classes.sideTextBlock}>
                    <p className={classes.titleText}>Want more info?</p>
                    <p className={classes.smallerText}>Visit our Github Repository</p>
                    <IconButton
                        variant="transparent"
                        className={classes.githubLogo}
                    >
                        <a
                            href="https://github.com/Bananabloon/NextListen"
                            target="_blank"
                        >
                            <img src="/icons/github/github-mark-white.svg" />
                        </a>
                    </IconButton>
                </div>
            </Group>
        </>
    );
};

export default HomePage;
