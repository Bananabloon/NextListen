import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";
import Header from "../../organisms/Header/Header";

const ApplicationTemplate = (): React.JSX.Element => {
    return (
        <Fluid style={{ height: "100%" }}>
            <Header />
            <Outlet />
        </Fluid>
    );
};

export default ApplicationTemplate;
