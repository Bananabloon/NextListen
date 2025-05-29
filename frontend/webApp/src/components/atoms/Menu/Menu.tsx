import React, { createContext, useContext, useState } from "react";
import classes from "./Menu.module.css";
import cs from "classnames";
import Dropdown from "../Dropdown/Dropdown";

interface MenuProps extends React.HTMLAttributes<HTMLDivElement> {}

interface MenuContextType {
    isOpen: boolean;
    toggle: () => void;
    close: () => void;
}

const MenuContext = createContext<MenuContextType | undefined>(undefined);

const useMenuContext = () => {
    const context = useContext(MenuContext);
    if (!context) {
        throw new Error("Menu components must be used within a Menu");
    }
    return context;
};

const Menu = ({ children, className, ...props }: MenuProps): React.JSX.Element => {
    const [isOpen, setIsOpen] = useState(false);

    const toggle = () => setIsOpen((o) => !o);
    const close = () => setIsOpen(false);

    return (
        <MenuContext.Provider value={{ isOpen, toggle, close }}>
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
    const { toggle } = useMenuContext();

    return (
        <div
            className={classes.target}
            onClick={toggle}
        >
            {children}
        </div>
    );
};

Menu.Dropdown = ({ children }: { children: React.ReactNode }) => {
    const { isOpen, close } = useMenuContext();

    if (!isOpen) return null;

    return <Dropdown onClick={() => close()}>{children}</Dropdown>;
};

export default Menu;
