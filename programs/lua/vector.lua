Vector = {x = nil, y = nil}

function Vector:length()
    return math.sqrt(self.x^2 + self.y^2)
end

function Vector:angle()
    return (math.atan(self.x / self.y) * 180) / math.pi
end

function Vector:add(v2)
    return Vector:create(self.x + v2.x, self.y + v2.y)
end

function Vector:sub(v2)
    return Vector:create(self.x - v2.x, self.y - v2.y)
end

function Vector:mult(n)
    return Vector:create(self.x * n , self.y * n)
end

function Vector:unit(n)
    local scale = n or 1
    local length = self:length()
    return Vector:create((self.x/length)*scale, (self.y/length)*scale)
end

function Vector:normal(n)
    return Vector:create(-self.y, self.x):unit(n)
end

function Vector:copy()
    return Vector:create(self.x, self.y)
end

function Vector:dot(v1, v2)
    return v1.x*v2.x + v1.y*v2.y
end

function Vector:cross(v1, v2)
    return v1.x*v2.y - v1.y*v2.x
end

function Vector:create(x, y) 
    local newVec = {}
    newVec.x = x or 0
    newVec.y = y or x or 0

    --Assign vectorm methods to the new vector
    newVec.length = Vector.length
    newVec.angle = Vector.angle
    newVec.add = Vector.add
    newVec.sub = Vector.sub
    newVec.mult = Vector.mult
    newVec.unit = Vector.unit
    newVec.normal = Vector.normal
    newVec.copy = Vector.copy

    --Pre-calculate angle & length
    newVec.length = newVec:length()
    newVec.angle = newVec:angle()

    return newVec
end


--[[DEBUG
local v1 = Vector:create(0, 1)
local v2 = Vector:create(1, 0)
local v3 = Vector:create(0, 0)
local a = 0
local b = 0

print("-----")
print("v1", v1.x, v1.y)
print("v2", v2.x, v2.y)
print("v3", v3.x, v3.y)
print("a", a)
print("b", b)
print("Vec", Vector.x, Vector.y)

v3 = v3:add(v2)
v3 = v3:add(v1)
a = v3.l

print("-----")
print("v1", v1.x, v1.y)
print("v2", v2.x, v2.y)
print("v3", v3.x, v3.y)
print("a", a)
print("b", b)
print("Vec", Vector.x, Vector.y)
]]