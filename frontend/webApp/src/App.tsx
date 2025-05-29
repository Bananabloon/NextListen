import { createBrowserRouter, createRoutesFromElements, Navigate, Route, RouterProvider } from "react-router-dom";
import HomePage from "./pages/HomePage/HomePage";
import HomeTemplate from "./components/templates/HomeTemplate/HomeTemplate";
import ApplicationTemplate from "./components/templates/ApplicationTemplate/ApplicationTemplate";
import DiscoveryPage from "./pages/DiscoveryPage/DiscoveryPage";

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route>
            <Route
                path="/callback"
                element={<Navigate to="/discovery" />}
            />
            <Route element={<ApplicationTemplate />}>
                <Route
                    path="/discovery"
                    element={<DiscoveryPage />}
                />
            </Route>
            <Route element={<HomeTemplate />}>
                <Route
                    path="/"
                    element={<HomePage />}
                />
            </Route>
        </Route>
    )
);

function App() {
    return <RouterProvider router={router} />;
}

export default App;
