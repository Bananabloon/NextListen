import { IconCompass, IconTestPipe } from "@tabler/icons-react";
import { PageConfig } from "../types/config.types";

const PAGE_CONFIG: PageConfig = {
    "/discovery": {
        path: "/discovery",
        title: "Discovery Queue",
        icon: IconCompass,
    },
    "/test": {
        path: "/test",
        title: "Test",
        icon: IconTestPipe,
    },
};

export default PAGE_CONFIG;
