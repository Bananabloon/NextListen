import { useState } from "react";
import Stack from "../../components/atoms/Stack/Stack";
import QueueGenerateOverlay from "../../components/molecules/QueueGenerateOverlay/QueueGenerateOverlay";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
import { useQueue } from "../../contexts/QueueContext";
import QueueLoadingOverlay from "../../components/organisms/QueueLoadingOverlay/QueueLoadingOverlay";
const DiscoveryPage = (): React.JSX.Element => {
    const [show, setShow] = useState(false);
    const { loading } = useQueue();

    return (
        <Stack className={classes.container}>
            {loading ? <QueueLoadingOverlay /> : <SongCardConveyor className={classes.conveyor} />}

            <QueueGenerateOverlay show={show} />
            {/* <div id="test-y"></div> */}
        </Stack>
    );
};

export default DiscoveryPage;
