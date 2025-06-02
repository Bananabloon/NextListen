import classes from "./Group.module.css";
import cs from "classnames";

interface GroupProps extends React.HTMLAttributes<HTMLDivElement> {}

const Group = ({ children, className, ...props }: GroupProps): React.JSX.Element => {
    return (
        <div
            className={cs(classes.group, className)}
            {...props}
        >
            {children}
        </div>
    );
};

export default Group;
