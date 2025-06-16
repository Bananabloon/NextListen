import Button from "../../atoms/Button/Button";
import IconButton from "../../atoms/IconButton/IconButton";
import Stack from "../../atoms/Stack/Stack";
import classes from "./AppInformationView.module.css";

interface AppInformationViewProps extends React.HTMLAttributes<HTMLDivElement> {}

const AppInformationView = ({ children, className, ...props }: AppInformationViewProps): React.JSX.Element => {
    return (
        <Stack
            className={classes.main}
            {...props}
        >
            <h1 className={classes.sectionTitle}>Application & Session</h1>
            <Stack className={classes.container}>
                <p style={{ fontSize: "var(--font-size-xxl)" }}>
                    Version: 1.0.0 <span style={{ color: "var(--text-color-dimmed)" }}>(Dev)</span>{" "}
                </p>
                <p style={{ color: "var(--text-color-dimmed)" }}>Last updated: 16.06.2025</p>
                <IconButton
                    variant="transparent"
                    style={{ paddingLeft: "0" }}
                >
                    <a
                        href="https://github.com/Bananabloon/NextListen"
                        target="_blank"
                    >
                        <img src="/icons/github/github-mark-white.svg" />
                    </a>
                </IconButton>

                <Button
                    className={classes.sessionClearButton}
                    onClick={() => sessionStorage.clear()}
                >
                    Clear Session Storage
                </Button>
            </Stack>
        </Stack>
    );
};

export default AppInformationView;
