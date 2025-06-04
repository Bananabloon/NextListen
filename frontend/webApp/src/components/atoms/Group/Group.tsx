import React from "react";
import classes from "./Group.module.css";
import cs from "classnames";

interface GroupProps extends React.HTMLAttributes<HTMLDivElement> {}

const Group = React.forwardRef<HTMLDivElement, GroupProps>(({ children, className, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cs(classes.group, className)}
            {...props}
        >
            {children}
        </div>
    );
});
export default Group;
