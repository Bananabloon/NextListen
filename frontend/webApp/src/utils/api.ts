import { trim } from "lodash";

// ! important to have a slash at the end because DJANGO
// django by default forwards requests without slash at the end
// and it messes up with nginx and omg im so tired already
export const normalizePath = (url: string = "") => {
    const [path, query] = url.split("?");
    return `/${trim(path, "/")}/${query ? `?${query}` : ""}`;
};
