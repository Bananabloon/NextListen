import { useState } from "react";
import Stack from "../../components/atoms/Stack/Stack";
import QueueGenerateOverlay from "../../components/molecules/QueueGenerateOverlay/QueueGenerateOverlay";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
const DiscoveryPage = (): React.JSX.Element => {
    const [show, setShow] = useState(false);
    return (
        <Stack className={classes.container}>
            <SongCardConveyor className={classes.conveyor} />
            <QueueGenerateOverlay show={show} />
        </Stack>
    );
};

export default DiscoveryPage;
