import { ErrorConfig } from "../types/config.types";

const ERRORS = {
    _400_BAD_REQUEST: {
        code: 400,
        variant: "BAD_REQUEST",
        title: "Bad Request",
        message: "The request was invalid. Check your input and try again.",
    },
    _401_TOKEN_EXPIRED: {
        code: 401,
        variant: "TOKEN_EXPIRED",
        title: "Session Expired",
        message: "Your session has expired. Please log in again.",
    },
    _401_INVALID_TOKEN: {
        code: 401,
        variant: "INVALID_TOKEN",
        title: "Invalid Token",
        message: "Your login token is invalid. Please try logging in again.",
    },
    _403_PREMIUM_REQUIRED: {
        code: 403,
        variant: "PREMIUM_REQUIRED",
        title: "Spotify Premium Required",
        message:
            "To use this application, a Spotify Premium account is required. This limitation is set by Spotify and applies to all apps using certain features of their service.",
    },
    _404_NOT_FOUND: {
        code: 404,
        variant: "NOT_FOUND",
        title: "Not Found",
        message: "The requested resource could not be found.",
    },
    _429_RATE_LIMITED: {
        code: 429,
        variant: "RATE_LIMITED",
        title: "Too Many Requests",
        message: "You're sending too many requests. Please slow down.",
    },
    _500_INTERNAL_ERROR: {
        code: 500,
        variant: "INTERNAL_ERROR",
        title: "Server Error",
        message: "An unexpected error occurred. Please try again later.",
    },
    _600_CLIENT_RENDER_ERROR: {
        code: 600,
        variant: "CLIENT_RENDER_ERROR",
        title: "Something Went Wrong",
        message: "An unexpected error occurred in the app. Please refresh the page or try again later.",
    },
};

export const DEFAULT_VARIANTS: Record<number, string> = {
    400: "BAD_REQUEST",
    401: "TOKEN_EXPIRED",
    403: "PREMIUM_REQUIRED",
    404: "NOT_FOUND",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
};

export const getErrorKey = (code: number, variant?: string) => {
    return `_${code}_${(variant || DEFAULT_VARIANTS[code] || "").toUpperCase()}`;
};

export const getError = (code: number, variant?: string) => {
    return ERRORS[getErrorKey(code, variant)];
};

export default ERRORS;
