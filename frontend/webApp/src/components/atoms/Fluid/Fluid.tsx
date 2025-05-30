import classes from './Fluid.module.css';
import cs from 'classnames';

interface FluidProps extends React.HTMLAttributes<HTMLDivElement> {}

const Fluid = ({ children, className, ...props }: FluidProps): React.JSX.Element => {
    return (
        <div className={cs(classes.fluid, className)} {...props}>
            {children}
        </div>
    );
};

export default Fluid;
