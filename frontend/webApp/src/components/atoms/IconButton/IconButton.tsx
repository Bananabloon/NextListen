import { Size } from "../../../types/component.types";
import classes from "./IconButton.module.css";
import cs from "classnames";

interface IconButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
    size?: Size;
    variant?: "default" | "transparent" | "filled";
    disabled?: boolean;
}

const IconButton = ({
    children,
    className,
    size = "md",
    variant = "default",
    disabled = false,
    ...props
}: IconButtonProps): React.JSX.Element => {
    return (
        <button
            className={cs(classes.button, className)}
            data-size={size}
            data-variant={variant}
            disabled={disabled}
            {...props}
        >
            {children}
        </button>
    );
};

export default IconButton;
