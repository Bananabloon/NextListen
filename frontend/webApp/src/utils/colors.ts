export function hexToRgb(hex: string) {
    const normalizedHex = hex.replace("#", "");
    const bigint = parseInt(normalizedHex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return [r, g, b];
}

// based on human perceived brightness formula
export function getBrightestColor(hexColors: string[]) {
    function brightness([r, g, b]: number[]) {
        return 0.299 * r + 0.587 * g + 0.114 * b;
    }

    return hexColors.reduce((brightest, current) => {
        const currentBrightness = brightness(hexToRgb(current));
        const brightestBrightness = brightness(hexToRgb(brightest));
        return currentBrightness > brightestBrightness ? current : brightest;
    });
}
