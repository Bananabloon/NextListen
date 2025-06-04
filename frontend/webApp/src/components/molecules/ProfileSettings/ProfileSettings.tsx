import useFetch from "../../../hooks/useFetch";
import Avatar from "../../atoms/Avatar/Avatar";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileSettings.module.css";
import cs from "classnames";
import { IconLockOpen } from "@tabler/icons-react";
import useRequests from "../../../hooks/useRequests";
import { useEffect } from "react";

interface ProfileSettingsProps extends React.HTMLAttributes<HTMLDivElement> {}
const unlinkSpotify = () => {
    return;
    // const requests = useRequests();
    // requests.sendRequest("POST", "/");
};
const ProfileSettings = ({ children, className, ...props }: ProfileSettingsProps): React.JSX.Element => {
    const { loading, data, error } = useFetch("/spotify/profile");
    return (
        <div
            className={cs(classes.container, className)}
            {...props}
        >
            <div className={classes.accountContainer}>
                <Group>
                    <Stack className={classes.userTextContainer}>
                        <h1 className={classes.usernameText}>{data?.display_name}</h1>
                        <p className={classes.emailText}>{data?.email} </p>
                    </Stack>
                    <Avatar
                        src={data?.images?.[0]?.url}
                        className={classes.profilePicture}
                        size={168}
                    />
                </Group>
                <Group>
                    <Button
                        onClick={() => unlinkSpotify()}
                        style={{ backgroundColor: "#E60F32" }}
                    >
                        <IconLockOpen className={classes.openLockIcon} />
                        Unlink Spotify
                    </Button>
                    <Button style={{ backgroundColor: "#E60F32" }}>
                        <IconLockOpen className={classes.openLockIcon} />
                        Remove Data
                    </Button>
                </Group>
            </div>
        </div>
    );
};

export default ProfileSettings;
