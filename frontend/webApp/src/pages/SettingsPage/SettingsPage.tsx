import { useNavigate } from "react-router-dom";
import Button from "../../components/atoms/Button/Button";
import Group from "../../components/atoms/Group/Group";
import Stack from "../../components/atoms/Stack/Stack";
import classes from "./SettingsPage.module.css";
import { IconSettings } from "@tabler/icons-react";
import AppInformationView from "../../components/molecules/AppInformationView/AppInformationView";
import StatsView from "../../components/molecules/StatsView/StatsView";
import ProfileView from "../../components/molecules/ProfileView/ProfileView";
import MiniPlayer from "../../components/molecules/MiniPlayer/MiniPlayer";
const SettingsPage = (): React.JSX.Element => {
    const navigate = useNavigate();
    return (
        <Stack className={classes.main}>
            <Group className={classes.header}>
                <IconSettings
                    size={38}
                    style={{ alignSelf: "self-start", marginTop: "6px" }}
                />
                <h1 className={classes.title}>Settings</h1>
                <MiniPlayer className={classes.miniPlayer} />
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
