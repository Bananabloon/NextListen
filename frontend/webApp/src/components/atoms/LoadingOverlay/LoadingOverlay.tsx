import { SyncLoader } from "react-spinners";
import classes from "./LoadingOverlay.module.css";
import cs from "classnames";

interface LoadingOverlayProps extends React.HTMLAttributes<HTMLDivElement> {}

const LoadingOverlay = ({ children, className, ...props }: LoadingOverlayProps): React.JSX.Element => {
    return (
        <div
            className={cs(classes.container, className)}
            {...props}
        >
            <SyncLoader color="var(--primary-color-7)" />
        </div>
    );
};

export default LoadingOverlay;
