import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import Stack from "../../atoms/Stack/Stack";
import classes from "./AppInformationView.module.css";
import cs from "classnames";

interface AppInformationViewProps extends React.HTMLAttributes<HTMLDivElement> {}

const AppInformationView = ({ children, className, ...props }: AppInformationViewProps): React.JSX.Element => {
    return (
        <Stack
            className={className}
            {...props}
        >
            <h1 className={classes.sectionTitle}>App Information</h1>
            <Stack className={classes.container}>
                <h2 className={classes.innerTextBig}>Version: 1.0.0</h2>
                <IconButton variant="transparent">
                    <a
                        href="https://github.com/Bananabloon/NextListen"
                        target="_blank"
                    >
                        <img src="/icons/github/github-mark-white.svg" />
                    </a>
                </IconButton>
            </Stack>
        </Stack>
    );
};

export default AppInformationView;
