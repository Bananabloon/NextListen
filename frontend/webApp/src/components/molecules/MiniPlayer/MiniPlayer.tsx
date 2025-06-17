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
    return (
        <Group className={cs(classes.miniPlayer, className)}>
            <ScrollingText className={classes.songTitle}>{currentState?.track_window.current_track.name}</ScrollingText> <br />
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
        </Group>
    );
};

export default MiniPlayer;
