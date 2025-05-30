import { Navigate, Outlet } from "react-router-dom";
import React from "react";
import useFetch from "../../hooks/useFetch";
import LoadingOverlay from "../atoms/LoadingOverlay/LoadingOverlay";

const AuthenticationWrapper = (): React.JSX.Element => {
    const { error, loading, data: user } = useFetch("/spotify/profile");

    if (loading) return <LoadingOverlay />;
    if (!error && user) return <Outlet />;
    if (error?.status && (error?.status === 401 || error?.status >= 500)) {
        console.error(error);
    }
    return <Navigate to={"/login"} />;
};

export default AuthenticationWrapper;
