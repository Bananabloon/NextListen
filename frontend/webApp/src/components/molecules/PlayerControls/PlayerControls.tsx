import {
    IconPlayerPauseFilled,
    IconPlayerPlayFilled,
    IconPlayerTrackNextFilled,
    IconPlayerTrackPrevFilled,
    IconRocket,
    IconThumbDown,
    IconThumbDownFilled,
    IconThumbUp,
    IconThumbUpFilled,
} from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import { usePlayback } from "../../../contexts/PlaybackContext";

const PlayerControls = ({ ...props }): React.JSX.Element => {
    const [feedback, saved, curveballs] = [-1, false, false];
    const { currentState, player } = usePlayback();

    return (
        <Group {...props}>
            <IconButton
                size="md"
                variant="transparent"
            >
                {feedback === -1 ? (
                    <IconThumbDownFilled style={{ transform: "scaleX(-1) translateY(2px)" }} />
                ) : (
                    <IconThumbDown style={{ transform: "scaleX(-1) translateY(2px)" }} />
                )}
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
            >
                {feedback === 1 ? (
                    <IconThumbUpFilled
                        style={{
                            transform: "translateY(-2px)",
                        }}
                    />
                ) : (
                    <IconThumbUp
                        style={{
                            transform: "translateY(-2px)",
                        }}
                    />
                )}
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => player.previousTrack()}
            >
                <IconPlayerTrackPrevFilled />
            </IconButton>
            <IconButton
                size="sm"
                variant="filled"
                style={{ borderRadius: "50%" }}
                onClick={() => player.togglePlay()}
            >
                {currentState?.paused ? <IconPlayerPlayFilled /> : <IconPlayerPauseFilled />}
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => player.nextTrack()}
            >
                <IconPlayerTrackNextFilled />
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
            >
                <img src={`/icons/spotify/like-icon-like${saved ? "d" : ""}.svg`} />
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
            >
                {curveballs ? (
                    <IconRocket />
                ) : (
                    <img
                        src={`/icons/tabler/rocket-x.svg`}
                        style={{ filter: "invert(100%)" }}
                    />
                )}
            </IconButton>
        </Group>
    );
};

export default PlayerControls;
