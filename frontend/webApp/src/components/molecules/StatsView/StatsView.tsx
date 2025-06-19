import useFetch from "../../../hooks/useFetch";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./StatsView.module.css";
interface StatsViewProps extends React.HTMLAttributes<HTMLDivElement> {}

const StatsView = ({ children, className, ...props }: StatsViewProps): React.JSX.Element => {
    const { data } = useFetch("/spotify/user-stats");
    return (
        <Group className={classes.main}>
            <Stack style={{ width: "225px" }}>
                <p style={{ fontSize: "var(--font-size-lg)" }}>Reactions</p>
                <p className={classes.statText}>
                    Songs liked: <span style={{ color: "var(--text-color)" }}>{data?.liked ? data.liked : "-"}</span>
                </p>
                <p
                    className={classes.statText}
                    style={{ marginBottom: "var(--spacing-sm)" }}
                >
                    Songs disliked: <span style={{ color: "var(--text-color)" }}>{data?.disliked ? data.disliked : "-"}</span>
                </p>
            </Stack>
            <Stack style={{ width: "225px" }}>
                <p style={{ fontSize: "var(--font-size-lg)" }}>Top artists</p>
                <ul style={{ listStyle: "none" }}>
                    {data?.top_artists ? (
                        (data?.top_artists).map((artist, i) => {
                            artist = `#${i + 1} ${artist[0]}`;
                            return (
                                <li
                                    key={i}
                                    className={classes.statTextSide}
                                >
                                    {artist}
                                </li>
                            );
                        })
                    ) : (
                        <p className={classes.placeholder}>No artists to display.</p>
                    )}
                </ul>
            </Stack>
        </Group>
    );
};

export default StatsView;
