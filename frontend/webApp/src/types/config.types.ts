import { TablerIcon } from "@tabler/icons-react";

export interface PageData {
    path: string;
    title: string;
    icon: TablerIcon;
}

export interface PageConfig {
    [path: string]: PageData;
}

export interface ErrorConfig {
    code: number;
    variant: string;
    title: string;
    message: string;
}
