function padBeforeString(string, length, padding_char) {
    return Array(length - String(string).length).fill(padding_char).join("") + String(string);
}

function padAfterString(string, length, padding_char) {
    return String(string) + Array(length - String(string).length).fill(padding_char).join("");
}

function decToBin(number) {
    let bin = Number(number).toString(2);
    return padBeforeString(bin, WORD_SIZE, "0");
}

function binToDec(bin_number) {
    out = 0;
    for (let i = 0; i < bin_number.length; i++) {
        out += Math.pow(2, i) * Number(bin_number[bin_number.length - i - 1])
    }
    return out;
}