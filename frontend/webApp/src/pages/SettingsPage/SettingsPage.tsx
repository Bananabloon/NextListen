import { Navigate, useNavigate } from "react-router-dom";
import Button from "../../components/atoms/Button/Button";
import Group from "../../components/atoms/Group/Group";
import Stack from "../../components/atoms/Stack/Stack";
import ProfileSettings from "../../components/molecules/ProfileSettings/ProfileSettings";
import StatsDisplay from "../../components/molecules/StatsDisplay/StatsDisplay";
import classes from "./SettingsPage.module.css";
import { IconSettings } from "@tabler/icons-react";
const SettingsPage = (): React.JSX.Element => {
    //navigate -1
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
            <Group className={classes.content}>
                <ProfileSettings />
                <StatsDisplay />
            </Group>
        </Stack>
    );
};

export default SettingsPage;
