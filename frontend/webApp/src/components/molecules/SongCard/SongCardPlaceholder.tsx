import cs from "classnames";
import Stack from "../../atoms/Stack/Stack";
import classes from "./SongCard.module.css";

interface SongCardPlaceholderProps extends React.HTMLAttributes<HTMLDivElement> {
    transparent?: boolean;
}

const SongCardPlaceholder = ({
    transparent = false,
    children,
    className,
    ...props
}: SongCardPlaceholderProps): React.JSX.Element => {
    return (
        <Stack
            className={cs(classes.card)}
            style={{ visibility: transparent ? "hidden" : "visible" }}
            {...props}
        >
            {children}
        </Stack>
    );
};

export default SongCardPlaceholder;
