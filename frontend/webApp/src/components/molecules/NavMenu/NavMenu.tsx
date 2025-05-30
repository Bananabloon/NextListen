import { IconList, IconListTree } from "@tabler/icons-react";
import Menu from "../../atoms/Menu/Menu";
import classes from "./NavMenu.module.css";
import cs from "classnames";
import Group from "../../atoms/Group/Group";
import PageTitle from "../PageTitle/PageTitle";
import { useState, useMemo } from "react";
import PAGE_CONFIG from "../../../config/pages.config";
import _ from "lodash";
import Button from "../../atoms/Button/Button";
import { Link, useLocation } from "react-router-dom";

interface NavMenuProps extends React.HTMLAttributes<HTMLDivElement> {}

const NavMenu = ({ children, className, ...props }: NavMenuProps): React.JSX.Element => {
    const location = useLocation();

    const navLinks = useMemo(
        () =>
            _.values(PAGE_CONFIG).map((page, i) => (
                <Link
                    to={page.path}
                    key={i}
                >
                    <Button
                        variant="menu"
                        style={
                            page.path === location.pathname
                                ? {
                                      color: "var(--primary-color-3)",
                                      backgroundColor: "var(--background-color-4)",
                                  }
                                : {}
                        }
                        leftSection={<page.icon />}
                    >
                        {page.title}
                    </Button>
                </Link>
            )),
        [location.pathname]
    );

    return (
        <Menu
            className={cs(classes.container, className)}
            {...props}
        >
            <Menu.Target>
                <Group>
                    <IconList
                        size={42}
                        stroke={1.5}
                    />

                    <PageTitle />
                </Group>
            </Menu.Target>
            <Menu.Dropdown style={{ width: "250px" }}>{navLinks}</Menu.Dropdown>
        </Menu>
    );
};

export default NavMenu;
