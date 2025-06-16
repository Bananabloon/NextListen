import { useNavigate } from "react-router-dom";
import Button from "../../components/atoms/Button/Button";
import Group from "../../components/atoms/Group/Group";
import Stack from "../../components/atoms/Stack/Stack";
import ProfileSettings from "../../components/molecules/ProfileSettings/ProfileSettings";
import classes from "./SettingsPage.module.css";
import { IconSettings } from "@tabler/icons-react";
import AppInformationView from "../../components/molecules/AppInformationView/AppInformationView";
import StatsView from "../../components/molecules/StatsView/StatsView";

const SettingsPage = (): React.JSX.Element => {
    const navigate = useNavigate();
    return (
        <Stack className={classes.container}>
            <Group className={classes.header}>
                <IconSettings
                    size={38}
                    style={{ alignSelf: "self-start", marginTop: "6px" }}
                />
                <h1 className={classes.title}>Settings</h1>

                <Button
                    className={classes.returnButton}
                    size="lg"
                    onClick={() => navigate(-1)}
                >
                    Return
                </Button>
            </Group>
            <Group style={{ gap: "0", width: "900px" }}>
                <Stack className={classes.content}>
                    <ProfileSettings />
                    <AppInformationView />
                </Stack>
                <StatsView />
            </Group>
        </Stack>
    );
};

export default SettingsPage;
