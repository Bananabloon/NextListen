import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";
import Header from "../../organisms/Header/Header";
import classes from "./ApplicationTemplate.module.css";
import Footer from "../../organisms/Footer/Footer";

const ApplicationTemplate = (): React.JSX.Element => {
    return (
        <Fluid className={classes.layout}>
            <Header />
            <Outlet />
            <Footer />
        </Fluid>
    );
};

export default ApplicationTemplate;
