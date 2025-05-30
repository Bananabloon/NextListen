import { API_URL } from "../config/url.config.ts";
import { normalizePath } from "../utils/api.ts";

type Method = "GET" | "HEAD" | "POST" | "PUT" | "DELETE" | "CONNECT" | "OPTIONS" | "TRACE" | "PATCH";

interface useRequestsReturn {
    getPath: (path: string) => string;
    sendRequest: (
        method: Method,
        path: string,
        options?: RequestInit,
        errorCallback?: (response: Response) => void
    ) => Promise<any>;
}

export const useRequests = (): useRequestsReturn => {
    const getPath = (path: string): string => (API_URL ? `${API_URL}${normalizePath(path)}` : "");

    const refreshTokens = async () => {
        return await sendRequest("POST", "auth/spotify/refresh-token");
    };

    const handleRequestError = async (response: Response) => {
        let errorBody = await response.text().catch(() => "Unable to read error body");
        console.error(`Request failed [${response.status}]`, errorBody);
    };

    const sendRequest = async (
        method: Method,
        path: string,
        options: RequestInit = {},
        errorCallback: (response: Response) => void = handleRequestError
    ) => {
        const url = getPath(path);

        const fetchOptions = {
            Accept: "application/json",
            "Content-Type": "application/json",
            Credentials: "include",
            "Access-Control-Allow-Origin": "*",
            ...options,
            method,
        };

        const getServiceUnavailableResponse = () =>
            new Response(JSON.stringify({ detail: "No response from server" }), {
                status: 503,
                headers: { "Content-Type": "application/json" },
            });

        const fetchData = () => fetch(url, fetchOptions).catch(getServiceUnavailableResponse);

        let response = await fetchData();

        if (response.status == 401) {
            await refreshTokens();
            response = await fetchData();
        }

        if (!response.ok) {
            // cloning resolves issues with body reading
            const clonedResponse = response.clone();
            return errorCallback(clonedResponse);
        }
        // handle no content reponses
        let json = {};
        try {
            json = (await response?.json?.()) ?? {};
        } catch (err) {
            console.error(`Couldn't parse request response. URL=${url}`, err);
        }

        return json;
    };

    return { getPath, sendRequest };
};

export default useRequests;
