import Stack from "../../components/atoms/Stack/Stack";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
import { useQueue } from "../../contexts/QueueContext";
import QueueLoadingOverlay from "../../components/organisms/QueueLoadingOverlay/QueueLoadingOverlay";
import { useEffect } from "react";
import { isEmpty } from "lodash";
import PROJECT_DEFAULTS from "../../config/project.config";

const DiscoveryPage = (): React.JSX.Element => {
    const { queue, loading, createNewDiscoveryQueue, restoreDiscoveryQueue } = useQueue();

    useEffect(() => {
        restoreDiscoveryQueue("top", { count: PROJECT_DEFAULTS.QUEUE_LENGTH });
    }, []);

    return (
        <Stack className={classes.container}>
            {isEmpty(queue) || loading ? <QueueLoadingOverlay /> : <SongCardConveyor className={classes.conveyor} />}
        </Stack>
    );
};

export default DiscoveryPage;
