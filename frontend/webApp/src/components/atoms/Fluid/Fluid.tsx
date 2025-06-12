import React from "react";
import classes from "./Fluid.module.css";
import cs from "classnames";

interface FluidProps extends React.HTMLAttributes<HTMLDivElement> {}

const Fluid = React.forwardRef<HTMLDivElement, FluidProps>(({ children, className, ...props }, ref): React.JSX.Element => {
    return (
        <div
            className={cs(classes.fluid, className)}
            ref={ref}
            {...props}
        >
            {children}
        </div>
    );
});

export default Fluid;
