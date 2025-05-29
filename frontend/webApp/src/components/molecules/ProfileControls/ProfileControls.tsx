import { IconLogout, IconSettings } from "@tabler/icons-react";
import useFetch from "../../../hooks/useFetch";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Menu from "../../atoms/Menu/Menu";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileControls.module.css";
import Avatar from "../../atoms/Avatar/Avatar";

interface ProfileControlsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileControls = ({ className, ...props }: ProfileControlsProps): React.JSX.Element => {
    const { loading, data, error } = useFetch("/spotify/profile");

    return (
        <Menu
            className={className}
            {...props}
        >
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
            <Menu.Dropdown>
                <Button
                    className={classes.menuButton}
                    leftSection={<IconSettings size={20} />}
                >
                    Settings
                </Button>
                <Button
                    className={classes.menuButton}
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
