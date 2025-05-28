import { Size } from "../../../types/component.types";
import Group from "../Group/Group";
import classes from "./Button.module.css";
import cs from "classnames";

interface ButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
    size?: Size;
    leftSection?: React.ReactNode;
    rightSection?: React.ReactNode;
    variant?: "default" | "spotify";
}

const Button = ({
    children,
    className,
    size = "md",
    variant = "default",
    leftSection,
    rightSection,
    ...props
}: ButtonProps): React.JSX.Element => {
    return (
        <button
            className={cs(classes.button, className)}
            data-size={size}
            data-variant={variant}
            {...props}
        >
            <Group style={{ alignItems: "center" }}>
                <div className={classes.section}>{leftSection}</div>
                {children}
                <div className={classes.section}>{rightSection}</div>
            </Group>
        </button>
    );
};

export default Button;
