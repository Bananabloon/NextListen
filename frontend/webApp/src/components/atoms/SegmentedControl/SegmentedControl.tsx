import React, { useState } from "react";
import classes from "./SegmentedControl.module.css";
import cs from "classnames";
import Group, { GroupProps } from "../Group/Group";
import Button, { ButtonProps } from "../Button/Button";
import { Size } from "../../../types/component.types";

interface SegmentedControlProps<T extends string> extends Omit<GroupProps, "onChange"> {
    options: {
        label: string;
        value: T;
        buttonProps?: ButtonProps; // props for individual buttons
    }[];
    value?: T;
    onChange?: (value: T) => void;
    radius?: Size;
    buttonProps?: ButtonProps; // props for all buttons
}

const SegmentedControl = <T extends string>({
    buttonProps,
    radius = "md",
    onChange,
    options,
    value,
    children,
    className,
    ...props
}: SegmentedControlProps<T>): React.JSX.Element => {
    const [selected, setSelected] = useState<T | undefined>(value);

    const handleClick = (option: T) => {
        setSelected(option);
        onChange?.(option);
    };

    return (
        <Group
            className={cs(classes.container, className)}
            style={{ "--segmented-control-radius": `var(--radius-${radius})` } as React.CSSProperties}
            {...props}
        >
            {options.map((option, i) => (
                <Button
                    key={i}
                    onClick={() => handleClick(option.value)}
                    data-selected={value ? value === option.value : selected === option.value}
                    {...buttonProps}
                    {...option.buttonProps}
                    className={cs(classes.button, buttonProps?.className, option.buttonProps?.className)}
                >
                    <span>{option.label}</span>
                </Button>
            ))}
        </Group>
    );
};

export default SegmentedControl;
