import Group from "../../atoms/Group/Group";
import ProfileControls from "../../molecules/ProfileControls/ProfileControls";
import classes from "./Header.module.css";

const Header = (): React.JSX.Element => {
    return (
        <Group className={classes.header}>
            <></>
            <ProfileControls style={{ marginLeft: "auto" }} />
        </Group>
    );
};

export default Header;
