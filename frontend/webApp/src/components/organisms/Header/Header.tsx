import Group from "../../atoms/Group/Group";
import NavMenu from "../../molecules/NavMenu/NavMenu";
import PageTitle from "../../molecules/PageTitle/PageTitle";
import ProfileControls from "../../molecules/ProfileControls/ProfileControls";
import classes from "./Header.module.css";

const Header = (): React.JSX.Element => {
    return (
        <Group className={classes.header}>
            <NavMenu />
            <ProfileControls style={{ marginLeft: "auto" }} />
        </Group>
    );
};

export default Header;
