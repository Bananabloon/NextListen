import useFetch from "../../../hooks/useFetch";
import Avatar from "../../atoms/Avatar/Avatar";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileSettings.module.css";
import { IconLockOpen } from "@tabler/icons-react";
import useRequests from "../../../hooks/useRequests";
import { useNavigate } from "react-router-dom";
import ModalController from "../ModalController/ModalController";

interface ProfileSettingsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileSettings = ({ children, className, ...props }: ProfileSettingsProps): React.JSX.Element => {
    const { data } = useFetch("/spotify/profile");
    const navigate = useNavigate();

    const deleteUserData = () => {
        const requests = useRequests();
        requests.sendRequest("DELETE", "/auth/spotify/delete-user-data");
        requests.sendRequest("DELETE", "/auth/spotify/delete-tokens");
        navigate("/login");
    };

    return (
        <Stack
            {...props}
            className={className}
        >
            <h1 className={classes.sectionTitle}>Account</h1>
            <Group className={classes.container}>
                <Stack className={classes.dataContainer}>
                    <h1 className={classes.usernameText}>{data?.display_name}</h1>
                    <p className={classes.emailText}>{data?.email} </p>
                    <ModalController
                        width={600}
                        height={300}
                        buttonContent={<>Remove Data</>}
                        buttonProps={{
                            leftSection: <IconLockOpen />,
                            className: classes.modalOpenButton,
                        }}
                    >
                        <Stack className={classes.modal}>
                            <h1 className={classes.modalTitle}>Are you sure?</h1>
                            <span className={classes.modalText}>
                                This action <span style={{ color: "#E60F32" }}>cannot be undone</span>.
                            </span>
                            <ul className={classes.warningList}>
                                <li className={classes.modalText}>Your data will be lost.</li>
                                <li className={classes.modalText}>Your account will be unlinked from NextListen.</li>
                            </ul>
                            <Button
                                onClick={deleteUserData}
                                size="lg"
                                className={classes.modalConfirmButton}
                            >
                                Confirm
                            </Button>
                        </Stack>
                    </ModalController>
                </Stack>
                <Avatar
                    src={data?.images?.[0]?.url}
                    className={classes.profilePicture}
                    size={192}
                />
            </Group>
        </Stack>
    );
};

export default ProfileSettings;
