import { useEffect, useState } from "react";
import useRequests from "./useRequests";

const useFetch = (path: string, options: object | undefined = undefined, cleanBeforeRefresh = false) => {
    const [data, setData] = useState<any | null>(null);
    const [error, setError] = useState<Response | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [refreshValue, setRefreshValue] = useState<boolean>(false);

    const refresh = () => {
        setRefreshValue((prev) => !prev);
    };

    const { sendRequest } = useRequests();

    useEffect(() => {
        const fetchData = async () => {
            if (cleanBeforeRefresh) {
                setData(null);
            }
            setError(null);
            setLoading(true);

            const onError = (response: Response) => {
                setData(null);
                setError(response);
                setLoading(false);
            };

            const json = await sendRequest("GET", path, options, onError);

            if (!json) return;
            setData(json);
            setError(null);
            setLoading(false);
        };
        fetchData();
    }, [path, options, refreshValue]);

    return { loading, error, data, refresh };
};

export default useFetch;
