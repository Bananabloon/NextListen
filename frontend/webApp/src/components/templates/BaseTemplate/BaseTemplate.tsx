import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";

const BaseTemplate = (): React.JSX.Element => {
    return (
        <Fluid>
            <Outlet />
        </Fluid>
    );
};

export default BaseTemplate;
