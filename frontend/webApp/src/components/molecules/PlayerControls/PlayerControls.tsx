import {
    IconPlayerPauseFilled,
    IconPlayerPlayFilled,
    IconPlayerTrackNextFilled,
    IconPlayerTrackPrevFilled,
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
import VolumeSeekBar from "../VolumeSeekBar/VolumeSeekBar";
import { isNull } from "lodash";

const PlayerControls = ({ ...props }): React.JSX.Element => {
    const { currentState, playNext, playPrevious, togglePlay } = usePlayback();
    const [feedback, setFeedback] = useState<Feedback>(0);
    const { sendRequest } = useRequests();

    useEffect(() => {
        sendRequest("GET", `songs/feedback/?spotify_uri=${currentState?.track_window.current_track.uri}`).then(
            (data) => {
                setFeedback(data?.feedback_value ?? 0);
            }
        );
    }, [currentState?.track_window.current_track.uri]);

    const updateFeedback = (value: Feedback) => {
        setFeedback(value);
        sendRequest("POST", "songs/feedback/update", {
            body: JSON.stringify({ spotify_uri: currentState?.track_window.current_track.uri, feedback_value: value }),
        });
    };

    return (
        <>
            <Group {...props}>
                <div style={{ width: "80px" }}></div>
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
                    size="md"
                    variant="transparent"
                    onClick={() => playNext()}
                >
                    <IconPlayerTrackNextFilled />
                </IconButton>
                <IconButton
                    size="md"
                    variant="transparent"
                >
                    <img src={`/icons/spotify/like-icon-like${false ? "d" : ""}.svg`} />
                </IconButton>
                <VolumeSeekBar />
            </Group>
        </>
    );
};

export default PlayerControls;
