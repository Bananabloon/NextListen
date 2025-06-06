import { IconList } from "@tabler/icons-react";
import cs from "classnames";
import _ from "lodash";
import { useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import PAGE_CONFIG from "../../../config/pages.config";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Menu from "../../atoms/Menu/Menu";
import PageTitle from "../../atoms/PageTitle/PageTitle";
import classes from "./NavMenu.module.css";

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
                        className={classes.navButton}
                        data-active={page.path === location.pathname}
                        leftSection={<page.icon />}
                    >
                        {page.title}
                    </Button>
                </Link>
            )),
        [location.pathname]
    );

    return (
        <Menu {...props}>
            <Menu.Target>
                <Group className={cs(classes.target, className)}>
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
