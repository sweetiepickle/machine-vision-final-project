import cv2 as cv 
import numpy as np 
from PIL import Image  
from tkinter.filedialog import askopenfilename

#---------------------------------------------------------------------------------------------
def GrayAVG(imgPIL):

    # make sure all the input images be converted to RGB
    imgPIL = imgPIL.convert('RGB')
    
    # Storage Image
    avg = Image.new ( imgPIL.mode , imgPIL.size )

    w = avg.size [0] 
    h = avg.size [1]

    for x in range(w) :
        for y in range(h):
        
            R , G , B = imgPIL.getpixel((x,y))
            
            # avg : grayscale = ( r + g + b) / 3
            gray = np.uint8 (( R + G + B ) / 3 )
            
            avg.putpixel (( x , y ) , ( gray , gray , gray ))

    return avg

def BinaryConvert(GrayImg):

    #Storage Image
    binary = Image.new(GrayImg.mode, GrayImg.size)

    #Get size
    width = GrayImg.size[0]
    height = GrayImg.size[1]

    #Loop
    for x in range(width):
        for y in range(height): 
            
            R,G,B = GrayImg.getpixel((x,y))  

            if (R < 127):
                binary.putpixel((x,y),(255,255,255)) # White
            else:
                binary.putpixel((x,y),(0,0,0))       # Black

    return binary

def ProcessingImage(filehinh):
    
    img = cv.imread(filehinh,cv.IMREAD_COLOR)
    imgPIL = Image.open(filehinh)

    # convert to grayscale
    avg = GrayAVG(imgPIL)

    # convert to binary and then invert the values
    binary_img = BinaryConvert(avg)

    binary_img = np.array(binary_img)
    # convert an image from one color space to another
    binary_img = cv.cvtColor(binary_img, cv.COLOR_BGRA2GRAY)

    # Tìm đường biên viền ngoài với giá trị trả về là mảng numpy (N,1,2) với N là số điểm 
    # Trong đường viền và mỗi điểm được biểu diễn dưới tọa độ (x,y) 
    contours,_= cv.findContours(binary_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)  
    # draw the 1st hierachy contour with thickness = 15 10 5
    Fcontour = cv.drawContours(binary_img, contours, 0, (255, 255, 255), 15)
 
    # Tô đen các đường viền còn lại
    Fcontour = cv.drawContours(Fcontour, contours[1:],-1,(0,0,0),10)

    ke = 5
    kernel = np.ones((ke, ke), np.uint8) 

    # Làm dày các đường viền sau đó thu nhỏ và làm mất đặc điểm của đối tượng trong hình ảnh
    # Để loại bỏ nhiễu và tách biệt đối tượng
    # dilation and erosion
    dilation = cv.dilate(Fcontour, kernel, iterations=2)
    erosion = cv.erode(dilation, kernel, iterations=2)

    # extract the absolute difference between dilation and erosion algorithms
    road = cv.absdiff(dilation, erosion)

    # invert binary values
    road_inv = cv.bitwise_not(road)

    # detach r g b
    b, g, r = cv.split(img)

    # Hai kênh màu đỏ và đen sẽ bị ghi đè bỏi mặt nạ
    r = cv.bitwise_and(r, r, mask=road_inv)
    b = cv.bitwise_and(b, b, mask=road_inv)

    #  Cho phép hiển thị hình ảnh với các kênh màu đã được xử lý 
    #  Và chỉ giữ lại thành phần màu xanh dương
    image_final = cv.merge((b, g, r))

    return image_final

#---------------------------------------------------------------------------------------------
# URL Image
filehinh = askopenfilename(filetypes=[("All files","*.*")])
image_final = ProcessingImage(filehinh)
cv.imshow('Maze', cv.imread(filehinh))
cv.imshow('Solution', image_final)
#-------------------------------------------------------------------------------------------------
cv.waitKey()
cv.destroyAllWindows()