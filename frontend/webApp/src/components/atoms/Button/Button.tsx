import { Size } from "../../../types/component.types";
import Group from "../Group/Group";
import classes from "./Button.module.css";
import cs from "classnames";

export interface ButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
    size?: Size;
    leftSection?: React.ReactNode;
    rightSection?: React.ReactNode;
    variant?: "default" | "transparent" | "subtle" | "spotify" | "menu";
    disabled?: boolean;
    background?: string;
}

const Button = ({
    children,
    className,
    size = "md",
    variant = "default",
    leftSection,
    rightSection,
    disabled = false,
    background,
    style,
    ...props
}: ButtonProps): React.JSX.Element => {
    return (
        <button
            className={cs(classes.button, className)}
            data-size={size}
            data-variant={variant}
            disabled={disabled}
            style={{ "--background": background, ...style } as React.CSSProperties}
            {...props}
        >
            <Group className={classes.content}>
                <div className={classes.section}>{leftSection}</div>
                {children}
                <div className={classes.section}>{rightSection}</div>
            </Group>
        </button>
    );
};

export default Button;
