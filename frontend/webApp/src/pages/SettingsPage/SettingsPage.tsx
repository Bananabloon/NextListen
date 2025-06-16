import { useNavigate } from "react-router-dom";
import Button from "../../components/atoms/Button/Button";
import Group from "../../components/atoms/Group/Group";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./SettingsPage.module.css";
import {
    IconPlayerPauseFilled,
    IconPlayerPlayFilled,
    IconPlayerTrackNextFilled,
    IconPlayerTrackPrevFilled,
    IconSettings,
} from "@tabler/icons-react";
import AppInformationView from "../../components/molecules/AppInformationView/AppInformationView";
import StatsView from "../../components/molecules/StatsView/StatsView";
import ProfileView from "../../components/molecules/ProfileView/ProfileView";
import { usePlayback } from "../../contexts/PlaybackContext";
import IconButton from "../../components/atoms/IconButton/IconButton";
import { isNull } from "lodash";
const SettingsPage = (): React.JSX.Element => {
    const { playNext, playPrevious, currentState, togglePlay } = usePlayback();
    const navigate = useNavigate();
    return (
        <Stack className={classes.main}>
            <Group className={classes.header}>
                <IconSettings
                    size={38}
                    style={{ alignSelf: "self-start", marginTop: "6px" }}
                />
                <h1 className={classes.title}>Settings</h1>

                <Group className={classes.miniPlayer}>
                    <p>{currentState?.track_window.current_track.name}</p> <br />
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
                </Group>

                <Button
                    className={classes.returnButton}
                    size="lg"
                    onClick={() => navigate(-1)}
                >
                    Return
                </Button>
            </Group>
            <Stack className={classes.sectionStack}>
                <Group className={classes.firstRow}>
                    <ProfileView />
                    <AppInformationView />
                </Group>

                <StatsView />
            </Stack>
        </Stack>
    );
};

export default SettingsPage;
