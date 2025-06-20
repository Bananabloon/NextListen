import Button from "../../atoms/Button/Button";
import IconButton from "../../atoms/IconButton/IconButton";
import Stack from "../../atoms/Stack/Stack";
import classes from "./AppInformationView.module.css";
import packageJson from "../../../../package.json";
interface AppInformationViewProps extends React.HTMLAttributes<HTMLDivElement> {}

const AppInformationView = ({ children, className, ...props }: AppInformationViewProps): React.JSX.Element => {
    let appVersion = packageJson.version;
    return (
        <Stack
            className={classes.main}
            {...props}
        >
            <h1 className={classes.sectionTitle}>Application & Session</h1>
            <Stack className={classes.container}>
                <p className={classes.versionText}>
                    Version: {appVersion} <span style={{ color: "var(--text-color-dimmed)" }}>(Dev)</span>{" "}
                </p>
                <p className={classes.updateDateText}>Last updated: 19.06.2025</p>
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
