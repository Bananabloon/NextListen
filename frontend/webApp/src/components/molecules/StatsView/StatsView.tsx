import useFetch from "../../../hooks/useFetch";
import Stack from "../../atoms/Stack/Stack";
import classes from "./StatsView.module.css";
interface StatsViewProps extends React.HTMLAttributes<HTMLDivElement> {}

const StatsView = ({ children, className, ...props }: StatsViewProps): React.JSX.Element => {
    const { data } = useFetch("/spotify/user-stats");
    return (
        <Stack
            className={classes.content}
            {...props}
        >
            <Stack className={classes.container}>
                <p className={classes.statText}>
                    Songs liked: <span style={{ color: "var(--text-color)" }}>{data?.liked}</span>
                </p>
                <p
                    className={classes.statText}
                    style={{ marginBottom: "var(--spacing-sm)" }}
                >
                    Songs disliked: <span style={{ color: "var(--text-color)" }}>{data?.disliked}</span>
                </p>
                <p className={classes.statText}>Top artists:</p>
                {data?.top_artists ? (
                    (data?.top_artists).map((artist, i) => {
                        artist = `#${i + 1} ${artist[0]}`;
                        return <p className={classes.statTextSide}>{artist}</p>;
                    })
                ) : (
                    <p className={classes.placeholder}>No artists to display.</p>
                )}
            </Stack>
        </Stack>
    );
};

export default StatsView;
