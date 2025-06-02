import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";
import Header from "../../organisms/Header/Header";
import classes from "./ApplicationTemplate.module.css";
import Footer from "../../organisms/Footer/Footer";
import { PlaybackProvider } from "../../../contexts/PlaybackContext";

const ApplicationTemplate = (): React.JSX.Element => {
    return (
        <PlaybackProvider>
            <Fluid className={classes.layout}>
                <Header />
                <Outlet />
                <Footer />
            </Fluid>
        </PlaybackProvider>
    );
};

export default ApplicationTemplate;
