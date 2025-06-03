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
import { useEffect, useState } from "react";
import useRequests from "../../../hooks/useRequests";
import { Feedback } from "../../../types/api.types";

const PlayerControls = ({ ...props }): React.JSX.Element => {
    const { currentState, previousTrack, nextTrack, togglePlay } = usePlayback();
    const [feedback, setFeedback] = useState<Feedback>(0);
    const { sendRequest } = useRequests();

    useEffect(() => {
        sendRequest(
            "GET",
            "songs/song-feedback",
            JSON.stringify({ body: { spotify_uri: currentState?.track_window.current_track.uri } }) as RequestInit
        ).then((data) => setFeedback(data?.feedback_value ?? 0));
    }, [currentState?.track_window.current_track.uri]);

    const updateFeedback = (value: Feedback) => {
        setFeedback(value);
        sendRequest(
            "POST",
            "songs/song-feedback",
            JSON.stringify({
                body: {
                    spotify_uri: currentState?.track_window.current_track.uri,
                    feedback: value,
                },
            }) as RequestInit
        );
    };

    return (
        <Group {...props}>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => updateFeedback(feedback === -1 ? 0 : -1)}
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
                onClick={() => updateFeedback(feedback === 1 ? 0 : 1)}
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
                onClick={() => previousTrack()}
            >
                <IconPlayerTrackPrevFilled />
            </IconButton>
            <IconButton
                size="sm"
                variant="filled"
                style={{ borderRadius: "50%" }}
                onClick={() => togglePlay()}
            >
                {currentState?.paused ? <IconPlayerPlayFilled /> : <IconPlayerPauseFilled />}
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => nextTrack()}
            >
                <IconPlayerTrackNextFilled />
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
            >
                <img src={`/icons/spotify/like-icon-like${false ? "d" : ""}.svg`} />
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
            >
                {false ? (
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
