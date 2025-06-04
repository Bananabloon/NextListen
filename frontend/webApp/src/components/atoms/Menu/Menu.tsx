import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import classes from "./Menu.module.css";
import cs from "classnames";
import Dropdown, { DropdownProps } from "../Dropdown/Dropdown";
import Portal from "../Portal/Portal";
import { useViewportSize } from "@mantine/hooks";

interface MenuProps extends React.HTMLAttributes<HTMLDivElement> {
    opened?: boolean;
    setOpened?: (open: boolean | ((prev: boolean) => boolean)) => void;
}

interface MenuContextType {
    isOpen: boolean;
    toggle: () => void;
    close: () => void;
    targetRef: React.RefObject<HTMLDivElement | null>;
}

const MenuContext = createContext<MenuContextType | undefined>(undefined);

const useMenuContext = () => {
    const context = useContext(MenuContext);
    if (!context) {
        throw new Error(
            "Menu components must be used within a Menu.\n If you're in the development mode, this is probably caused by hot reload."
        );
    }
    return context;
};

const Menu = ({ children, className, opened, setOpened, ...props }: MenuProps): React.JSX.Element => {
    const isControlled = opened !== undefined && setOpened !== undefined;

    const [uncontrolledOpened, setUncontrolledOpened] = useState(false);
    const targetRef = useRef<HTMLDivElement>(null);

    const isOpen = isControlled ? opened : uncontrolledOpened;

    const setIsOpen = (value: boolean | ((prev: boolean) => boolean)) => {
        isControlled ? setOpened(value) : setUncontrolledOpened(value);
    };

    const toggle = () => setIsOpen((o) => !o);
    const close = () => setIsOpen(false);

    return (
        <MenuContext.Provider value={{ isOpen, toggle, close, targetRef }}>
            <div
                className={cs(classes.menu, className)}
                {...props}
            >
                {children}
            </div>
        </MenuContext.Provider>
    );
};

Menu.Target = ({ children }: { children: React.ReactNode }) => {
    const { toggle, targetRef } = useMenuContext();

    return (
        <div
            className={classes.target}
            onClick={toggle}
            ref={targetRef}
        >
            {children}
        </div>
    );
};

Menu.Dropdown = ({ children, style, className, ...props }: DropdownProps) => {
    const { isOpen, close, targetRef } = useMenuContext();
    const { width, height } = useViewportSize();
    const [dynamicStyle, setDynamicStyle] = useState<React.CSSProperties>({});

    useEffect(() => {
        if (isOpen && targetRef.current) {
            const rect = targetRef.current.getBoundingClientRect();
            setDynamicStyle({
                top: rect.bottom + window.scrollY,
                left: rect.left + window.scrollX,
                width: rect.width,
            });
        }
    }, [isOpen, targetRef, width, height]);

    if (!isOpen) return null;

    return (
        <Portal>
            <Dropdown
                className={cs(classes.dropdown, className)}
                style={{ ...dynamicStyle, ...style }}
                onClick={close}
                {...props}
            >
                {children}
            </Dropdown>
        </Portal>
    );
};

export default Menu;
