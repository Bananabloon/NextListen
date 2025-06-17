import useFetch from "../../../hooks/useFetch";
import Avatar from "../../atoms/Avatar/Avatar";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ProfileView.module.css";
import { IconTrashFilled } from "@tabler/icons-react";
import useRequests from "../../../hooks/useRequests";
import { useNavigate } from "react-router-dom";
import ModalController from "../ModalController/ModalController";
interface ProfileSettingsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileView = ({ children, className, ...props }: ProfileSettingsProps): React.JSX.Element => {
    const { data } = useFetch("/spotify/profile");
    const navigate = useNavigate();

    const deleteUserData = () => {
        const requests = useRequests();
        requests.sendRequest("DELETE", "/auth/spotify/delete-account");
        sessionStorage.clear();
        navigate("/");
    };

    return (
        <Stack
            {...props}
            className={classes.main}
        >
            <h1 className={classes.sectionTitle}>Account</h1>
            <Group className={classes.container}>
                <Stack className={classes.dataContainer}>
                    <h1 className={classes.usernameText}>{data?.display_name ? data.display_name : "Username"}</h1>
                    <p className={classes.emailText}>{data?.email ? data.email : "example@email.com"} </p>
                    <ModalController
                        width={600}
                        height={250}
                        buttonContent={<>Remove Data</>}
                        buttonProps={{
                            leftSection: <IconTrashFilled size={20} />,
                            className: classes.modalOpenButton,
                        }}
                    >
                        <Stack className={classes.modal}>
                            <h1 className={classes.modalTitle}>Are you sure?</h1>
                            <span>
                                This action{" "}
                                <span
                                    style={{
                                        color: "var(--danger-color )",
                                        fontWeight: 600,
                                    }}
                                >
                                    cannot be undone.
                                </span>
                            </span>
                            <ul className={classes.warningList}>
                                <li>Your data will be lost.</li>
                                <li>Your account will be unlinked from NextListen.</li>
                            </ul>
                            <Button
                                onClick={deleteUserData}
                                size="sm"
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

export default ProfileView;

