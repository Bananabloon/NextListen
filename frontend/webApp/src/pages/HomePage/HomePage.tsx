import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";

const HomePage = (): React.JSX.Element => {
    return (
        <Stack
            style={{
                justifyContent: "center",
                alignItems: "center",
                height: "100%",
            }}
        >
            <Button
                variant="spotify"
                size="lg"
                style={{
                    transform: "translateY(-50%)",
                }}
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
