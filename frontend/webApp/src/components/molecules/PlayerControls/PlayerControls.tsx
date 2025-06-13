import { IconPlayerPauseFilled, IconPlayerPlayFilled, IconPlayerTrackNextFilled, IconPlayerTrackPrevFilled } from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import { usePlayback } from "../../../contexts/PlaybackContext";
import VolumeSeekBar from "../VolumeSeekBar/VolumeSeekBar";
import { isNull } from "lodash";
import SaveOnSpotifyButton from "../SaveOnSpotifyButton/SaveOnSpotifyButton";
import FeedbackButtons from "../FeedbackButtons/FeedbackButtons";

const PlayerControls = ({ ...props }): React.JSX.Element => {
    const { currentState, playNext, playPrevious, togglePlay } = usePlayback();

    return (
        <>
            <Group {...props}>
                <div style={{ width: "140px" }}></div>
                <FeedbackButtons />
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
                <SaveOnSpotifyButton />
                <VolumeSeekBar />
            </Group>
        </>
    );
};

export default PlayerControls;
