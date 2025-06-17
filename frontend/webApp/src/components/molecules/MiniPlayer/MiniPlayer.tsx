import { IconPlayerPauseFilled, IconPlayerPlayFilled, IconPlayerTrackNextFilled, IconPlayerTrackPrevFilled } from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import classes from "./MiniPlayer.module.css";
import cs from "classnames";
import { isNull } from "lodash";
import { usePlayback } from "../../../contexts/PlaybackContext";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";

interface MiniPlayerProps extends React.HTMLAttributes<HTMLDivElement> {}

const MiniPlayer = ({ children, className, ...props }: MiniPlayerProps): React.JSX.Element => {
    const { playNext, playPrevious, currentState, togglePlay } = usePlayback();

    const artistText = currentState?.track_window.current_track.artists.map((artist) => artist.name).join(", ");

    return (
        <Group className={cs(classes.miniPlayer, className)}>
            {currentState?.track_window.current_track ? (
                <>
                    <ScrollingText className={classes.songTitle}>
                        {currentState?.track_window.current_track.name}
                        {"  "}
                        &middot;
                        {"  "}
                        <span style={{ color: "var(--text-color-dimmed)" }}>{artistText}</span>
                    </ScrollingText>{" "}
                    <IconButton
                        size="sm"
                        variant="transparent"
                        onClick={() => playPrevious()}
                    >
                        <IconPlayerTrackPrevFilled />
                    </IconButton>
                    <IconButton
                        size="sm"
                        variant="filled"
                        style={{ borderRadius: "50%" }}
                        onClick={() => togglePlay()}
                    >
                        {isNull(currentState) || currentState.paused ? <IconPlayerPlayFilled /> : <IconPlayerPauseFilled />}
                    </IconButton>
                    <IconButton
                        size="sm"
                        variant="transparent"
                        onClick={() => playNext()}
                    >
                        <IconPlayerTrackNextFilled />
                    </IconButton>
                </>
            ) : (
                <span className={classes.placeholder}>Current track missing</span>
            )}
        </Group>
    );
};

export default MiniPlayer;
