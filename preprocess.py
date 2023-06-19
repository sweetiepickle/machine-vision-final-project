import cv2
import numpy as np

#---Preprocess---#
def preprocess(input_image):
    #Convert to gray
    gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)   
    #Apply Gaussian Blur  
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  
    #Convert to binary and invert   
    binary_inv = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 5)
    #Find contours
    contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #Assuming the maze is made of 2 pieces
    #Get the biggest 2 contours for 2 pieces
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    #Dilate and Erode
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(binary_inv, cv2.MORPH_OPEN, kernel)
    dilated = cv2.dilate(morph, kernel, iterations=4)
    eroded = cv2.erode(dilated, kernel, iterations=4)
    binary_inv = cv2.bitwise_not(eroded)
    return binary_inv, contours
#---Maze corners---#
def find_maze_corners(binary_inv, contours):
    #Image corners
    image_height, image_width = binary_inv.shape[:2]
    image_corner_tl = (0, 0)  #Top-Left corner
    image_corner_tr = (image_width, 0)  #Top-Right corner
    image_corner_bl = (0, image_height)  #Bottom-Left corner
    image_corner_br = (image_width, image_height)  #Bottom-Right corner
    #Min distance
    min_distance_tl = float('inf')
    min_distance_tr = float('inf')
    min_distance_bl = float('inf')
    min_distance_br = float('inf')
    #Comparing distance to find Maze corners
    for contour in contours:
        for point in contour:
            point = tuple(point[0])
            #Distance from points on contour to image corners
            distance_tl = np.sqrt((point[0] - image_corner_tl[0]) ** 2 + (point[1] - image_corner_tl[1]) ** 2)
            distance_tr = np.sqrt((point[0] - image_corner_tr[0]) ** 2 + (point[1] - image_corner_tr[1]) ** 2)
            distance_bl = np.sqrt((point[0] - image_corner_bl[0]) ** 2 + (point[1] - image_corner_bl[1]) ** 2)
            distance_br = np.sqrt((point[0] - image_corner_br[0]) ** 2 + (point[1] - image_corner_br[1]) ** 2)
            #Maze corners = points with min distance to Image corners 
            if distance_tl < min_distance_tl:
                min_distance_tl = distance_tl
                maze_corner_tl = point
            if distance_tr < min_distance_tr:
                min_distance_tr = distance_tr
                maze_corner_tr = point
            if distance_bl < min_distance_bl:
                min_distance_bl = distance_bl
                maze_corner_bl = point
            if distance_br < min_distance_br:
                min_distance_br = distance_br
                maze_corner_br = point
    #Return Corners (x,y)
    return maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br

#---Perspective warp---#
def apply_perspective_warp(image, maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br):
    #
    x_t=maze_corner_tr[0]-maze_corner_tl[0]
    x_b=maze_corner_br[0]-maze_corner_bl[0]
    y_l=maze_corner_bl[1]-maze_corner_tl[1]
    y_r=maze_corner_br[1]-maze_corner_tr[1]
    if x_t>x_b: maze_width = x_t+50
    else:   maze_width =x_b+50
    if y_l>y_r: maze_height = y_l+50
    else:   maze_height = y_r+50
    
    #Adjust new maze corners for beter image 
    new_maze_corner_tl = (0, 10)
    new_maze_corner_tr = (maze_width-10, 10)
    new_maze_corner_bl = (0, maze_height-10)
    new_maze_corner_br = (maze_width-10, maze_height-10)

    #Matrix for perspective warp
    src_points = np.float32([maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br])
    dst_points = np.float32([new_maze_corner_tl, new_maze_corner_tr, new_maze_corner_bl, new_maze_corner_br])
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    #Apply perspective warp
    warped_image = cv2.warpPerspective(image, perspective_matrix, (maze_width, maze_height))
    return warped_image
'''
image = cv2.imread('cap0.jpg')
preprocessed_image, contours = preprocess(image)
#drawed_contour = cv2.drawContours(preprocessed_image,contours ,-1,(0,0,0),1)
maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br = find_maze_corners(preprocessed_image, contours)
warped_image = apply_perspective_warp(preprocessed_image, maze_corner_tl, maze_corner_tr, maze_corner_bl, maze_corner_br)
#cv2.imshow('image 1', drawed_contour)
cv2.imshow('image', warped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
