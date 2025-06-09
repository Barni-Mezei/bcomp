_matrix = {}

function createMatrix(width, height, char)
    newMatrix = {}
    newMatrix.width = width
    newMatrix.height = height
    char = char or " "

    for y = 0, height, 1 do
        newMatrix[y] = {}
        for x = 0, width, 1 do
            newMatrix[y][x] = char
        end
    end

    return newMatrix
end

function clearMatrix(char, matrix)
    local m = matrix or _matrix

    for y = 0, m.height, 1 do
        for x = 0, m.width, 1 do
            m[y][x] = char
        end
    end
end

function drawRect(x, y, w, h, char, matrix)
    local m = matrix or _matrix

    drawLine(x,y, x+w-1,y, char, m)
    drawLine(x+w-1,y, x+w-1,y+h-1, char, m)
    drawLine(x+w-1,y+h-1, x,y+h-1, char, m)
    drawLine(x,y+h-1, x,y, char, m)
end

function setWorkingMatrix(matrix)
    _matrix = matrix
end

function setPixel(x, y, char, matrix)
    local m = matrix or _matrix
    local x = math.floor(x)
    local y = math.floor(y)

    if x < 0 or x >= m.width or
    y < 0 or y >= m.height then
        return nil
    end

    m[y][x] = char
end

function getPixel(x, y, matrix)
    local m = matrix or _matrix
    local x = math.floor(x)
    local y = math.floor(y)

    if x < 0 or x >= m.width or
    y < 0 or y >= m.height then
        return nil
    end

    return m[y][x]
end

function renderMatrix(isCorrected, matrix, isFullscreen)
    local m = matrix or _matrix
    local isC = isCorrected or false
    local isF = isFullscreen or false
    local str = ""

    local screenW = getWidth() - 1
    if isC then screenW = screenW / 2 end
    screenW = math.floor(screenW)
    local pad_size = screenW - m.width
    local pad = repeatChar(" ", pad_size)

    for y = 0, m.height, 1 do
        for x = 0, m.width, 1 do
            str = str..m[y][x]
            if isC then
                str = str..m[y][x]
            end
        end

        if isF then
            if pad_size > 0 then
                str = str..pad
            end
        else
            str = str.."\n"
        end
    end

    write(str)
    --flush()
end

local function los(x0, y0, x1, y1, callback)
    local sx, sy, dx, dy
  
    if x0 < x1 then
      sx = 1
      dx = x1 - x0
    else
      sx = -1
      dx = x0 - x1
    end
  
    if y0 < y1 then
      sy = 1
      dy = y1 - y0
    else
      sy = -1
      dy = y0 - y1
    end
  
    local err, e2 = dx-dy, nil
  
    if not callback(x0, y0) then return false end
  
    while not(x0 == x1 and y0 == y1) do
        e2 = err + err

        if e2 > -dy then
          err = err - dy
          x0  = x0 + sx
        end

        if e2 < dx then
          err = err + dx
          y0  = y0 + sy
        end

        if not callback(x0, y0) then return false end
    end
  
    return true
end
  
local function line(x0, y0, x1, y1, callback)
    local points = {}
    local count = 0
    local result = los(
        x0,
        y0,
        x1,
        y1,
        function (x,y)
            if callback and not callback(x,y) then
                return false
            end

            count = count + 1
            points[count] = {x, y}
            return true
        end
    )
    
    return points, result
end

function drawLine(x0, y0, x1, y1, char, matrix)
    local m = matrix or _matrix

    points, _ = line(math.floor(x0), math.floor(y0), math.floor(x1), math.floor(y1))

    for index, p in pairs(points) do
        setPixel(p[1], p[2], char, m)
    end
end
