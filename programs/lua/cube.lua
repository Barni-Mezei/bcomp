function hasKey(table, key)
    return table[key] ~= nil
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


_matrix = {}

function createMatrix(width, height, base)
    newMatrix = {}
    newMatrix.width = width
    newMatrix.height = height

    for y = 0, height, 1 do
        newMatrix[y] = {}
        for x = 0, width, 1 do
            newMatrix[y][x] = base
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

    return m[y][x]
end

function renderMatrix(isCorrected, matrix)
    local m = matrix or _matrix
    local isC = isCorrected or false

    for y = 0, m.height, 1 do
        for x = 0, m.width, 1 do
            writeChar(m[y][x])
            if isC then
                writeChar(m[y][x])
            end
        end
        writeChar("\n")
    end

    flush()
end

-------------------
--  Main script  --
-------------------

counter = 0

screen_scale = 1
sw = math.floor(getWidth()*screen_scale / 2) - 1
sh = getHeight()*screen_scale
screen = createMatrix(sw, sh)
setWorkingMatrix(screen)

function update()
    counter = counter + 1

    local speed = 0.1
    local angle_y = (counter / 1) * speed
    local angle_x = (counter / 2) * speed
    local cube_size = math.min(sw, sh) * 0.8

    local center = {
        x = sw*0.49,
        y = sh*0.49,
    }

    local center_top = {
        x = 0,
        y = math.sin(angle_x - math.pi*0.5) * cube_size*0.33,
    }

    local center_bottom = {
        x = 0,
        y = math.sin(-angle_x + math.pi*0.5) * cube_size*0.33,
    }

    local scale = {
        x = cube_size*0.49,
        y = math.sin(angle_x) * cube_size*0.5,
    }

    local x = {
        center_top.x + math.cos(angle_y + math.pi*0.0) * scale.x,
        center_top.x + math.cos(angle_y + math.pi*0.5) * scale.x,
        center_top.x + math.cos(angle_y + math.pi*1.0) * scale.x,
        center_top.x + math.cos(angle_y + math.pi*1.5) * scale.x,

        center_bottom.x + math.cos(angle_y + math.pi*0.0) * scale.x,
        center_bottom.x + math.cos(angle_y + math.pi*0.5) * scale.x,
        center_bottom.x + math.cos(angle_y + math.pi*1.0) * scale.x,
        center_bottom.x + math.cos(angle_y + math.pi*1.5) * scale.x,
    }

    local y = {
        center_top.y + math.sin(angle_y + math.pi*0.0) * scale.y,
        center_top.y + math.sin(angle_y + math.pi*0.5) * scale.y,
        center_top.y + math.sin(angle_y + math.pi*1.0) * scale.y,
        center_top.y + math.sin(angle_y + math.pi*1.5) * scale.y,

        center_bottom.y + math.sin(angle_y + math.pi*0.0) * scale.y,
        center_bottom.y + math.sin(angle_y + math.pi*0.5) * scale.y,
        center_bottom.y + math.sin(angle_y + math.pi*1.0) * scale.y,
        center_bottom.y + math.sin(angle_y + math.pi*1.5) * scale.y,
    }

    local z = {
        math.cos(angle_y + math.pi*0.5) * scale.x * math.cos(angle_x+math.pi*0.5) --[[ front]],
        math.cos(angle_y + math.pi*1.0) * scale.x * math.cos(angle_x+math.pi*0.5) --[[ front]],
        math.cos(angle_y + math.pi*1.5) * scale.x * math.cos(angle_x+math.pi*0.5) --[[ front]],
        math.cos(angle_y + math.pi*2.0) * scale.x * math.cos(angle_x+math.pi*0.5) --[[ front]],

        math.cos(angle_y + math.pi*0.5) * scale.x * math.cos(angle_x) --[[ front]],
        math.cos(angle_y + math.pi*1.0) * scale.x * math.cos(angle_x) --[[ front]],
        math.cos(angle_y + math.pi*1.5) * scale.x * math.cos(angle_x) --[[ front]],
        math.cos(angle_y + math.pi*2.0) * scale.x * math.cos(angle_x) --[[ front]],
    }


    for i, cz in pairs(z) do
        local z = cz + center.x
        z = z / 50

        x[i] = x[i] / z + center.x
        y[i] = y[i] / z + center.y
    end


    clearMatrix(" ")

    --Top
    drawLine(x[1], y[1], x[2], y[2], ".")
    drawLine(x[2], y[2], x[3], y[3], ".")
    drawLine(x[3], y[3], x[4], y[4], ".")
    drawLine(x[4], y[4], x[1], y[1], ".")

    --Bottom
    drawLine(x[5], y[5], x[6], y[6], ".")
    drawLine(x[6], y[6], x[7], y[7], ".")
    drawLine(x[7], y[7], x[8], y[8], ".")
    drawLine(x[8], y[8], x[5], y[5], ".")

    --Edges
    drawLine(x[1], y[1], x[5], y[5], ".")
    drawLine(x[2], y[2], x[6], y[6], ".")
    drawLine(x[3], y[3], x[7], y[7], ".")
    drawLine(x[4], y[4], x[8], y[8], ".")

    for i, coord_x in pairs(x) do
        setPixel(coord_x, y[i], "#")
    end

    clear()
    renderMatrix(true)

    delay(20)
    update()
end

update()