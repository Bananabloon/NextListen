import { createBrowserRouter, createRoutesFromElements, Navigate, Route, RouterProvider } from "react-router-dom";
import HomePage from "./pages/HomePage/HomePage";
import HomeTemplate from "./components/templates/HomeTemplate/HomeTemplate";
import ApplicationTemplate from "./components/templates/ApplicationTemplate/ApplicationTemplate";
import DiscoveryPage from "./pages/DiscoveryPage/DiscoveryPage";
import AuthenticationWrapper from "./components/wrappers/AuthenticationWrapper";
import LoginPage from "./pages/LoginPage/LoginPage";
import BaseTemplate from "./components/templates/BaseTemplate/BaseTemplate";
import SettingsPage from "./pages/SettingsPage/SettingsPage";

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<BaseTemplate />}>
            <Route element={<AuthenticationWrapper />}>
                <Route element={<ApplicationTemplate />}>
                    <Route
                        path="/discovery"
                        element={<DiscoveryPage />}
                    />
                    <Route
                        path="/test"
                        element={<></>}
                    />
                </Route>
                <Route
                    path="/settings"
                    element={<SettingsPage />}
                />
            </Route>
            <Route element={<HomeTemplate />}>
                <Route
                    path="/"
                    element={<HomePage />}
                />
                <Route
                    path="/login"
                    element={<LoginPage />}
                />
                <Route
                    path="/callback"
                    element={<Navigate to="/discovery" />}
                />
            </Route>
        </Route>
    )
);

function App() {
    return <RouterProvider router={router} />;
}

export default App;
