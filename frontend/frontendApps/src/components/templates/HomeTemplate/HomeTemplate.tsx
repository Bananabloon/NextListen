import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";

const HomeTemplate = (): React.JSX.Element => {
    return (
        <Fluid style={{ height: "100vh", padding: "var(--spacing-md)", background: "var(--background-color-1)" }}>
            <Outlet />
        </Fluid>
    );
};

export default HomeTemplate;
