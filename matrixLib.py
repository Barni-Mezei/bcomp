#This is a matrix libaray
from math import *
import os
import sys

#gray_scale = " .-x#@" #012345

gray_scale = " ░▒▓█" #01234

#Other (misc) matrix functions
def getWidthHeight(mat):
    m_height = len(mat)
    m_width = len(mat[0])

    return m_width, m_height

#Whole matrix functions
def createMatrix(width, height, fill_value = 0):
    mat = []

    for i in range(0, height):
        row = [fill_value for i in range(0, width)]
        mat.append(row)

    return mat

def replaceInMatrix(mat, from_value,to_value):
    m_width, m_height = getWidthHeight(mat)

    for y in range(m_height):
        for x in range(m_width):
            if mat[y][x] == from_value:
                mat[y][x] = to_value
    return

#Per pixel functions
def setpixelAt(mat, x,y, value):
    m_width, m_height = getWidthHeight(mat)

    clip_x = round( max(0, min(x, m_width - 1)) )
    clip_y = round( max(0, min(y, m_height- 1)) )

    mat[clip_y][clip_x] = value

def drawHLine(mat, start_x,start_y,width, value):
    clip_width = round( start_x+width )
    for x in range(start_x, clip_width):
        setpixelAt(mat, x, start_y, value)

def drawVLine(mat, start_x,start_y,height, value):
    clip_height = round( start_y+height )
    for y in range(start_y, clip_height):
        setpixelAt(mat, start_x, y, value)

def drawAxis(mat):
    m_width, m_height = getWidthHeight(mat)

    drawHLine(mat, 0,m_height/2,m_width, 1)
    drawVLine(mat, m_width/2,0,m_height, 1)
    setpixelAt(mat, m_width/2,m_height/2, 3)

def drawCircle(mat, center_x,center_y,r,start_angle,end_angle, value, resolution, isPerfect):
    c = pi/180

    for dir in range(start_angle,end_angle, resolution):
        px = center_x+sin(dir*c) * r
        py = center_y+cos(dir*c) * r

        if isPerfect:
            px = center_x+sin(dir*c) * r * 2

        setpixelAt(mat, px,py,value)

def drawRecangle(mat, start_x,start_y, width,height, value):
    drawHLine(mat, start_x, start_y, width-1, value) #top
    drawVLine(mat, start_x+width-1, start_y, height, value) #right
    drawHLine(mat, start_x, start_y+height-1, width-1, value) #bottom
    drawVLine(mat, start_x, start_y, height-1, value) # left

def fillRecangle(mat, start_x,start_y, width,height, value):
    m_width, m_height = getWidthHeight(mat)

    x2 = min(start_x+width, m_width)
    y2 = min(start_y+height, m_height)

    for x in range(start_x, x2):
        for y in range(start_y, y2):
            setpixelAt(mat, x, y, value)

#Rendering functions
def renderMatrix(mat, colors = gray_scale):
    str_out = ""
    for y in mat:
        row = ""
        for x in y:
            str_out += colors[ min(abs(x), len(colors)) ]
        str_out += "\n"

    sys.stdout.write(str_out)
    sys.stdout.flush()

#Run demo code
if __name__ == "__main__":
    col,row = os.get_terminal_size()

    w = 80
    h = row-2

    a = createMatrix(w, h, 0)
    width, height = getWidthHeight(a)

    drawRecangle(a, 0,0, width,height, 4)
    drawCircle(a, width/2,0,7, -90,90, 4, 2,True )
    drawCircle(a, width/2,height,7, 90,270, 4, 2,True )

    drawCircle(a, width/2,height/2,8, 0,360, 3, 2,True)

    drawHLine(a, 0,height/2, width, 4)

    renderMatrix(a)