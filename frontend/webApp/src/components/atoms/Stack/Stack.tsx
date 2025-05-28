import classes from './Stack.module.css';
import cs from 'classnames';

interface StackProps extends React.HTMLAttributes<HTMLDivElement> {}

const Stack = ({ children, className, ...props }: StackProps): React.JSX.Element => {
    return (
        <div className={cs(classes.stack, className)} {...props}>
            {children}
        </div>
    );
};

export default Stack;
