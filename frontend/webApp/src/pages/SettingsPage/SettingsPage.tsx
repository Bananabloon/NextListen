import { useNavigate } from "react-router-dom";
import Button from "../../components/atoms/Button/Button";
import Group from "../../components/atoms/Group/Group";
import Stack from "../../components/atoms/Stack/Stack";
import ProfileSettings from "../../components/molecules/ProfileSettings/ProfileSettings";
import classes from "./SettingsPage.module.css";
import { IconSettings } from "@tabler/icons-react";
import AppInformationView from "../../components/molecules/AppInformationView/AppInformationView";
const SettingsPage = (): React.JSX.Element => {
    const navigate = useNavigate();
    return (
        <Stack className={classes.container}>
            <Group className={classes.header}>
                <IconSettings
                    size={38}
                    style={{ alignSelf: "self-start", marginTop: "6px" }}
                />
                <h1 className={classes.title}>Application Settings</h1>

                <Button
                    className={classes.returnButton}
                    size="lg"
                    onClick={() => navigate(-1)}
                >
                    Return
                </Button>
            </Group>
            <Stack className={classes.content}>
                <ProfileSettings />
                <AppInformationView />
            </Stack>
        </Stack>
    );
};

export default SettingsPage;
