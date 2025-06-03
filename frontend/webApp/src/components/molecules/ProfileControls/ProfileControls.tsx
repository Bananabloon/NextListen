import { IconLogout, IconSettings } from "@tabler/icons-react";
import useFetch from "../../../hooks/useFetch";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Menu from "../../atoms/Menu/Menu";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileControls.module.css";
import Avatar from "../../atoms/Avatar/Avatar";
import useRequests from "../../../hooks/useRequests";
import { useNavigate } from "react-router-dom";

interface ProfileControlsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileControls = ({ className, ...props }: ProfileControlsProps): React.JSX.Element => {
    const { loading, data, error } = useFetch("/spotify/profile");
    const { sendRequest } = useRequests();
    const navigate = useNavigate();

    const logout = () => {
        sendRequest("POST", "/auth/spotify/delete-tokens");
        navigate("/");
    };
    const enterSettings = () => {
        navigate("/settings");
    };

    return (
        <Menu {...props}>
            <Menu.Target>
                <Group className={classes.container}>
                    <Stack className={classes.textStack}>
                        <span>logged in as</span>
                        <span>{!loading ? (data?.display_name ?? data?.email) : " "}</span>
                    </Stack>
                    <Avatar
                        src={data?.images?.[0]?.url}
                        className={classes.profilePicture}
                        size={64}
                    />
                </Group>
            </Menu.Target>
            <Menu.Dropdown className={classes.dropdown}>
                <Button
                    variant="menu"
                    onClick={enterSettings}
                    leftSection={<IconSettings size={20} />}
                >
                    Settings
                </Button>
                <Button
                    variant="menu"
                    onClick={logout}
                    leftSection={
                        <IconLogout
                            size={20}
                            style={{
                                transform: "translateX(2px)",
                            }}
                        />
                    }
                >
                    Log out
                </Button>
            </Menu.Dropdown>
        </Menu>
    );
};

export default ProfileControls;
