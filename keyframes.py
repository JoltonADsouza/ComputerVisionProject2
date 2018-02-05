from PIL import Image
import copy
import csv
import time
import numpy as np
import glob
image_list = []

## CONVERSION OF IMAGE TO GRAY FROM RGB
def rgb2gray(Image):
    r, g, b = Image[:,:,0], Image[:,:,1], Image[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

## STRUCTURAL SIMILARITY CALCULATOR FOR TWO IMAGES
def SSIM_Calculator(I_ref, I_next, width, height):
    height_resize = (int(height*0.5)); width_resize = (int(width*0.5))
    I_ref_resized = I_ref.resize((height_resize,width_resize), Image.ANTIALIAS); I_next_resized = I_next.resize((height_resize,width_resize), Image.ANTIALIAS)
    I_ref_array = np.asarray(I_ref_resized); I_next_array = np.asarray(I_next_resized);
    I_ref_resized = rgb2gray(I_ref_array); I_next_resized = rgb2gray(I_next_array)
    
    width_new, height_new = (Image.fromarray(I_ref_resized)).size    
    N = (height_new)*(width_new)
    k1 = 0.01;  k2 = 0.03; std_dev_I_ref = std_dev_I_next = Covariance_ref_next = 0  
    
    mean_int_I_ref = np.mean(I_ref_resized); mean_int_I_next = np.mean(I_next_resized)
    for i in range(0,height_new):
        for j in range(0,width_new):
            std_dev_I_ref = std_dev_I_ref + np.square(I_ref_resized[i][j]-mean_int_I_ref)
            std_dev_I_next = std_dev_I_next + np.square(I_next_resized[i][j]-mean_int_I_next)
            Covariance_ref_next = Covariance_ref_next + (I_ref_resized[i][j]-mean_int_I_ref)*(I_next_resized[i][j]-mean_int_I_next)      
    std_dev_I_ref = np.sqrt(std_dev_I_ref/(N-1))
    std_dev_I_next = np.sqrt(std_dev_I_next/(N-1))
    Covariance_ref_next = (Covariance_ref_next/N)
    C1 = k1*(2**8 - 1); C2 = k2*(2**8 - 1)   
    SSIM = ((2*(mean_int_I_ref*mean_int_I_next) + C1)*(2*Covariance_ref_next + C2)) / ((np.square(mean_int_I_ref) + np.square(mean_int_I_next) + C1)*(np.square(std_dev_I_ref) + np.square(std_dev_I_next) + C2))
    return SSIM



## START OF THE ALGORITHM

## READ IMAGES FROM THE SEQUENCE IN A LIST  
t0 = time.time()
for filename in glob.glob('C:/Users/Jolton/Desktop/Sequence2/*.jpg'): 
    im=Image.open(filename)
    image_list.append(im)
        
image = Image.open('C:/Users/Jolton/Desktop/Sequence2/000001.jpg')
width, height = image.size


## FINDING THE KEYFRAMES BY COMPARING THE IMAGES IN A STEP OF 10
I_next_index,index = 0,1; keyframes = []; keyframes.append(0)

for I_ref_index in range(0,len(image_list)-10,10):  
#    print(I_ref_index)
    I_next_index = I_ref_index+9;
    I_ref = image_list[I_ref_index]; I_next = image_list[I_next_index];
    SSIM = SSIM_Calculator(I_ref, I_next, width, height)
    if float(SSIM) < 0.575:
        for q in range(I_ref_index+1,I_next_index+1):
            I_temp = image_list[q]
                       
            SSIM_temp = SSIM_Calculator(I_ref, I_temp, width, height)
            
            if float(SSIM_temp) < 0.575:
                keyframes.append(q)
#                print(keyframes)
                break
# 
keyframes_copy = copy.copy(keyframes)
## FINDING THE KEYFRAMES THAT MATCH
similar_keyframes = [[] for i in range(len(keyframes))] ;clusters = [[] for i in range(len(keyframes))] ; scene_id_incrementer = 0; cluster_index = 0;

for i in range(0, len(keyframes)):
    if keyframes[i] == []:
        continue
    elif i == len(keyframes)-1:
        clusters[cluster_index].append(image_list[i])
    else:
        for a in range(keyframes_copy[i], keyframes_copy[i+1]):
            clusters[cluster_index].append(image_list[a])
            
        I_keyframe_ref = image_list[keyframes[i]]
        similar_keyframes[i].append(keyframes[i])
        similar_keyframes[i].append(chr(65+ scene_id_incrementer))
        for j in range(i+1,len(keyframes)):
            if keyframes[j] == []:
                continue
            else:
                I_keyframe_next = image_list[keyframes[j]]
                SSIM_keyframe_updated = SSIM_Calculator(I_keyframe_ref, I_keyframe_next, width, height);
                
                if float(SSIM_keyframe_updated) >= 0.75:
                    for b in range(keyframes_copy[j],keyframes_copy[j+1]):
                        clusters[cluster_index].append(image_list[b])
                    similar_keyframes[j].append(int(keyframes[j]+1))
                    similar_keyframes[j].append(chr(65+scene_id_incrementer))
                    keyframes[j] = [];
        cluster_index += 1
    scene_id_incrementer += 1;

## CREATING THE CSV FILE FOR THE RESULT
with open('Results.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    csv_writer.writerows([['Keyframes','Scene_id']])
    csv_writer.writerows(similar_keyframes)
    
t1 = time.time()
total_time = t1-t0
print("SUCCESFULL!!! \n Total Time Elapsed: ", total_time)        