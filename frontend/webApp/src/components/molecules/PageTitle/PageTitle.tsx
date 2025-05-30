import { useLocation } from "react-router-dom";
import PAGE_CONFIG from "../../../config/pages.config";
import classes from "./PageTitle.module.css";
import cs from "classnames";

interface PageTitleProps extends React.HTMLAttributes<HTMLSpanElement> {}

const PageTitle = ({ className, ...props }: PageTitleProps): React.JSX.Element => {
    const location = useLocation();
    const page = PAGE_CONFIG[location.pathname] ?? {};

    return (
        <span
            className={cs(classes.title, className)}
            {...props}
        >
            {page?.title ?? ""}
        </span>
    );
};

export default PageTitle;
