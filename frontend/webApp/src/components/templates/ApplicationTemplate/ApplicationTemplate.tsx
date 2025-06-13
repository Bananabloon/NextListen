import { Outlet } from "react-router-dom";
import Fluid from "../../atoms/Fluid/Fluid";
import Header from "../../organisms/Header/Header";
import classes from "./ApplicationTemplate.module.css";
import Footer from "../../organisms/Footer/Footer";
import { PlaybackProvider } from "../../../contexts/PlaybackContext";
import { QueueProvider } from "../../../contexts/QueueContext";

const ApplicationTemplate = (): React.JSX.Element => {
    return (
        <QueueProvider>
            <PlaybackProvider>
                <Fluid className={classes.layout}>
                    <Header />
                    <Outlet />
                    <Footer />
                </Fluid>
            </PlaybackProvider>
        </QueueProvider>
    );
};

export default ApplicationTemplate;
