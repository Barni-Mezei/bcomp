function clamp(value, min, max)
    return math.min(math.max(value, min), max)
end

function round(value)
    return math.floor(value + 0.5)
end

function roundTo(value, decimals)
    local scale = 10^decimals
    return round(value * scale) / scale
end

function roundToEven(value)
    local x = round(value)

    if x % 2 == 0 then return x end

    if x > 0 then
        return x + 1
    else
        return x - 1
    end
end