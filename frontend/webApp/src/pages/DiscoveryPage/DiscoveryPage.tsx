import Stack from "../../components/atoms/Stack/Stack";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
import { useQueue } from "../../contexts/QueueContext";
import QueueLoadingOverlay from "../../components/organisms/QueueLoadingOverlay/QueueLoadingOverlay";
import { useEffect } from "react";
import { isEmpty } from "lodash";

const DiscoveryPage = (): React.JSX.Element => {
    const { queue, loading, createNewDiscoveryQueue, restoreDiscoveryQueue } = useQueue();

    useEffect(() => {
        // if (isEmpty(queue)) createNewDiscoveryQueue("top", { count: 20 });
        // if (isEmpty(sessionStorage.getItem("queue"))) createNewDiscoveryQueue("top", { count: 20 });
        restoreDiscoveryQueue("top", { count: 20 });
    }, []);

    return (
        <Stack className={classes.container}>{loading ? <QueueLoadingOverlay /> : <SongCardConveyor className={classes.conveyor} />}</Stack>
    );
};

export default DiscoveryPage;
