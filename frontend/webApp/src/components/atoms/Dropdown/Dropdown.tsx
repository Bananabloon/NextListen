import classes from "./Dropdown.module.css";
import cs from "classnames";

interface DropdownProps extends React.HTMLAttributes<HTMLDivElement> {}

const Dropdown = ({ children, className, ...props }: DropdownProps): React.JSX.Element => {
    return (
        <div
            className={cs(classes.dropdown, className)}
            {...props}
        >
            <div className={classes.content}>{children}</div>
        </div>
    );
};

export default Dropdown;
