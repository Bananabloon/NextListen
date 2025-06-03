import { useNavigate, useRouteError } from "react-router-dom";
import { getError } from "../../config/errors.config";
import { ErrorConfig } from "../../types/config.types";
import useRequests from "../../hooks/useRequests";
import Button from "../../components/atoms/Button/Button";
import classes from "./ErrorBoundary.module.css";
import { AppError } from "../../utils/errors";
import Stack from "../../components/atoms/Stack/Stack";

const ErrorBoundary = (): React.JSX.Element => {
    const navigate = useNavigate();
    const { sendRequest } = useRequests();
    const error: AppError | any = useRouteError();

    const status = error?.status || 600;
    const variant = error?.variant;
    const errorConfig: ErrorConfig = getError(status, variant);
    const message = error?.overrideMessage ? error.message : errorConfig.message || error.message || "";
    const title = error?.overrideTitle ? error.title : errorConfig.title || error.title || "";

    const logout = async () => {
        await sendRequest("POST", "/auth/spotify/delete-tokens");
        navigate("/");
    };

    let onMainButtonClick: () => any, mainButtonMessage: string;

    switch (status) {
        case 401:
            onMainButtonClick = logout;
            mainButtonMessage = "Log in again";
            break;
        case 403:
            onMainButtonClick = logout;
            mainButtonMessage = "Use different account";
            break;
        case 404:
            onMainButtonClick = () => navigate(-1);
            mainButtonMessage = "Take me back";
            break;
        default:
            onMainButtonClick = () => navigate(0);
            mainButtonMessage = "Refresh page";
    }

    return (
        <>
            <div className={classes.background}>{status}</div>
            <Stack className={classes.center}>
                <Stack className={classes.details}>
                    <h1 className={classes.title}>{title}</h1>
                    <span className={classes.message}>{message}</span>
                </Stack>
                <Stack className={classes.buttons}>
                    <Button
                        onClick={onMainButtonClick}
                        size="lg"
                        variant="default"
                        style={{ background: "white", color: "black", fontWeight: 600 }}
                    >
                        {mainButtonMessage}
                    </Button>
                    <Button
                        onClick={() => navigate("/")}
                        size="md"
                        variant="transparent"
                    >
                        Return to home page
                    </Button>
                </Stack>
            </Stack>
        </>
    );
};

export default ErrorBoundary;
