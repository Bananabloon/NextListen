import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";

const ApplicationTemplate = (): React.JSX.Element => {
    return <Fluid style={{ background: "var(--background-color-1)" }}>{/* <Outlet /> */}</Fluid>;
};

export default ApplicationTemplate;
