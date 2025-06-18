import Stack from "../../components/atoms/Stack/Stack";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
import { useQueue } from "../../contexts/QueueContext";
import QueueLoadingOverlay from "../../components/organisms/QueueLoadingOverlay/QueueLoadingOverlay";
import { useEffect, useRef, useState } from "react";
import { isEmpty } from "lodash";
import PROJECT_DEFAULTS from "../../config/project.config";
import { VirtuosoHandle } from "react-virtuoso";

const DiscoveryPage = (): React.JSX.Element => {
    const { queue, loading, restoreDiscoveryQueue } = useQueue();
    const [shouldSnap, setShouldSnap] = useState(true);

    useEffect(() => {
        console.log("rerender");
        restoreDiscoveryQueue("top", { count: PROJECT_DEFAULTS.QUEUE_LENGTH });
        setShouldSnap(true);
    }, []);

    return (
        <Stack className={classes.container}>
            {isEmpty(queue) || loading ? (
                <QueueLoadingOverlay />
            ) : (
                <SongCardConveyor
                    shouldSnap={shouldSnap}
                    setShouldSnap={setShouldSnap}
                    className={classes.conveyor}
                />
            )}
        </Stack>
    );
};

export default DiscoveryPage;
