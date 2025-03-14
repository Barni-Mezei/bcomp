--[[
Dependencies:
- math
- matrix
]]

function distance(x1, y1, x2, y2)
    local dx = x2 - x1
    local dy = y2 - y1

    local dx2 = dx * dx
    local dy2 = dy * dy

    return math.sqrt(dx*dx + dy*dy)
end


function isInRect(x, y, rx, ry, rw, rh)
    return x > rx and x < rx+rw and y > ry and y < ry+rh
end

function collision(x, y)
    for i,w in pairs(map) do
        if isInRect(x, y, w.x, w.y, w.w, w.h) then return true end
    end

    return false
end

function castRays(distances, points)
    for r = -player.fov/2, player.fov/2, 1 do
        local angle = player.r + r

        local ray = {
            x = player.x + 0,
            y = player.y + 0,
            dx = math.cos(angle * math.pi/180) * player.step,
            dy = math.sin(angle * math.pi/180) * player.step,
            hit = false,
        }

        local cDist = 0
        while cDist < player.maxDist and not ray.hit do
            ray.x = ray.x + ray.dx
            ray.y = ray.y + ray.dy
            cDist = cDist + player.step

            ray.hit = collision(ray.x, ray.y)
        end
        


        --cDist = player.maxDist - distance(player.x, player.y, ray.x, ray.y)

        --Fish eye correction
        cDist = distance(player.x, player.y, ray.x, ray.y)
        cDist = cDist * math.cos((angle - player.r) * math.pi/180)
        cDist = player.maxDist - cDist

        table.insert(distances, cDist)
        table.insert(points, ray)
    end
end

function movePlayer(angle, speed)
    player.x = player.x + math.cos(angle * math.pi/180) * speed
    player.y = player.y + math.sin(angle * math.pi/180) * speed
end

function renderView(distances, colors)
    for i,d in pairs(distances) do
        local height = d * (sh/player.maxDist)
        local x = sw/2 - (#distances/2)*(sw/player.fov) + i*(sw/player.fov) + 0.5
        local y = sh/2 + height/2

        local distRatio = (d + 1) / (player.maxDist+1)
        local colorIndex = clamp(#colors - math.floor(#colors * distRatio) , 1, #colors)
        local char = string.sub(colors, colorIndex, colorIndex)

        drawLine(x,y, x,y-height, char)
    end
end

function renderMap(points)
    for i,r in pairs(map) do
        drawRect(r.x, r.y, r.w, r.h, "#")
    end

    setPixel(player.x, player.y, "@")

    local dirX = round( math.cos(player.r * math.pi/180) * 2 )
    local dirY = round( math.sin(player.r * math.pi/180) * 2 )

    setPixel(player.x + dirX, player.y + dirY, "*")

    --Render hipoints on map
    for i,p in pairs(points) do
        setPixel(p.x,p.y, "'")
    end
end

-------------------
--  Main script  --
-------------------

counter = 0

sw = math.floor(getWidth() / 2) - 1
sh = round(getHeight() + 1)
screen = createMatrix(sw, sh)
setWorkingMatrix(screen)

map = {
    {--Top wall
        x = 0,
        y = 0,
        w = 50,
        h = 2,
    },
    
    {--Bottom wall
        x = 0,
        y = 48,
        w = 50,
        h = 2,
    },

    {--Left wall
        x = 0,
        y = 2,
        w = 2,
        h = 46,
    },

    {--Right wall
        x = 48,
        y = 2,
        w = 2,
        h = 46,
    },

    --Other walls
    {
        x = 5,
        y = 5,
        w = 5,
        h = 5,
    },

    {
        x = 20,
        y = 5,
        w = 5,
        h = 10,
    },

    {
        x = 25,
        y = 10,
        w = 15,
        h = 5,
    },

    {
        x = 30,
        y = 30,
        w = 10,
        h = 15,
    },

    {
        x = 25,
        y = 30,
        w = 5,
        h = 5,
    },

    {
        x = 10,
        y = 20,
        w = 5,
        h = 25,
    },
}

player = {
    speed = 0.33,
    rotSpeed = 4,

    x = 20,
    y = 20,
    r = -90,
    fov = sw,
    maxDist = 30,
    step = 0.5,
}

function update()
    counter = counter + 1

    --Handle player controls
    if keyIsDown("w") then
        movePlayer(player.r, player.speed)
    end

    if keyIsDown("a") then
        movePlayer(player.r-90, player.speed)
    end

    if keyIsDown("s") then
        movePlayer(player.r+180, player.speed)
    end
    
    if keyIsDown("d") then
        movePlayer(player.r+90, player.speed)
    end

    if keyIsDown("left") then
        player.r = player.r - player.rotSpeed
    end

    if keyIsDown("right") then
        player.r = player.r + player.rotSpeed
    end

    --Cast rays & render result
    local distances = {}
    local points = {}
    castRays(distances, points)

    clearMatrix(" ")

    local colors = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'."
    --local colors = "@#0|-."
    --local colors = "*-"

    renderView(distances, colors)
    --renderMap(points)

    --Actually draw the current frame
    --clear()
    renderMatrix(true, screen, true)

    delay(20)
    update()
end

update()