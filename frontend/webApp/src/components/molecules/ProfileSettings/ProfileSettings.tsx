import useFetch from "../../../hooks/useFetch";
import Avatar from "../../atoms/Avatar/Avatar";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileSettings.module.css";
import cs from "classnames";
import { IconLockOpen } from "@tabler/icons-react";
import useRequests from "../../../hooks/useRequests";
import { useNavigate } from "react-router-dom";
import ModalController from "../ModalController/ModalController";

interface ProfileSettingsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileSettings = ({ children, className, ...props }: ProfileSettingsProps): React.JSX.Element => {
    const { loading, data, error } = useFetch("/spotify/profile");
    const navigate = useNavigate();

    const deleteUserData = () => {
        const requests = useRequests();
        requests.sendRequest("DELETE", "/auth/spotify/delete-user-data");
        requests.sendRequest("POST", "/auth/spotify/delete-tokens");
        navigate("/login");
    };

    return (
        <Group
            className={cs(classes.container, className)}
            {...props}
        >
            <Stack className={classes.dataContainer}>
                <h1 className={classes.usernameText}>{data?.display_name}</h1>
                <p className={classes.emailText}>{data?.email} </p>
                <ModalController
                    width={820}
                    height={360}
                    buttonStyle={{ backgroundColor: "#E60F32", marginLeft: "0", marginTop: "auto", marginBottom: "var(--spacing-lg)" }}
                    buttonContent={
                        <>
                            <IconLockOpen className={classes.openLockIcon} />
                            Remove Data
                        </>
                    }
                >
                    <Stack className={classes.modal}>
                        <h1 className={classes.modalTitle}>Are you sure?</h1>
                        <h2 className={classes.modalText}>
                            This action <span style={{ color: "#E60F32" }}>cannot be undone</span>. Your data will be lost.
                        </h2>
                        <h2 className={classes.modalText}>You will be logged out.</h2>
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
    );
};

export default ProfileSettings;
