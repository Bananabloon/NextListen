import ERRORS, { DEFAULT_VARIANTS, getErrorKey } from "../config/errors.config";
import { ErrorConfig } from "../types/config.types";

export class AppError extends Error {
    status: number = 600;
    message: string = "Could not construct AppError instance.";
    variant: string | undefined = undefined;
    title: string | undefined = undefined;

    // Overload signatures:
    constructor(response: Response, options?: { variant?: string });
    constructor(errorConfig: ErrorConfig);

    // Single implementation:
    constructor(arg1: Response | ErrorConfig, arg2?: { variant?: string }) {
        super();

        const responseConstructor = () => {
            const response = arg1 as Response;
            const variant = arg2?.variant;

            if (response.ok) {
                throw new Error("Cannot create an AppError from a successful response.");
            }

            const errorConfig: ErrorConfig = ERRORS[getErrorKey(response.status, variant)];

            this.status = errorConfig?.code || response.status;
            this.message = errorConfig.message;
            this.title = errorConfig.title;
            this.variant = variant || DEFAULT_VARIANTS[response.status];
        };

        const configConstructor = () => {
            const errorConfig = arg1 as ErrorConfig;

            this.status = errorConfig.code;
            this.message = errorConfig.message;
            this.title = errorConfig.title;
            this.variant = errorConfig.variant;
        };

        if (arg1 instanceof Response) responseConstructor();
        else configConstructor();
    }
}
