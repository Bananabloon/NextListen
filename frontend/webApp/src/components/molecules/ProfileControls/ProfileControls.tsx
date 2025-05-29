import useFetch from "../../../hooks/useFetch";
import Group from "../../atoms/Group/Group";
import classes from "./ProfileControls.module.css";
import cs from "classnames";

interface ProfileControlsProps extends React.HTMLAttributes<HTMLDivElement> {}

const ProfileControls = ({ className, ...props }: ProfileControlsProps): React.JSX.Element => {
    const { loading, data, error } = useFetch("/spotify/top-artists");

    console.log(loading, data, error);

    return (
        <Group
            className={cs(classes.container, className)}
            {...props}
        ></Group>
    );
};

export default ProfileControls;
