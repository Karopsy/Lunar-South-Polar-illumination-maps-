#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 17:56:42 2024

@author: louis
"""

import time
import requests
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import math
import pandas as pd
import os
import tifffile as tiff
import rasterio
from PIL import Image
import imageio.v2 as imageio
import cv2
import matplotlib.pyplot as plt
import sys
import argparse
import logging

###########################################################################################
###########################################################################################
############## CODE STARTS HERE - ALL THE FUNCTIONS #######################################v##########################
###########################################################################################

############# - Valid for all the evaluated sites - ##########################
def generate_date_list(start_date, hours_increment, days_increment, num_dates):
    date_list = []
    current_date = start_date
    
    for _ in range(num_dates):
        date_list.append(current_date)
        current_date += timedelta(hours=hours_increment)
    
    return date_list

def format_date_list(date_list):
    formatted_dates = [date.strftime('%Y-%m-%dT%H:%M:%S') for date in date_list]
    return formatted_dates

def format_date_list_save(date_list):
    formatted_dates_save = [date.strftime('%Y-%m-%dT%H_%M_%S') for date in date_list]
    return formatted_dates_save

def average_images(input_folder, year,  average_type, start_time, end_time):
    """
    Compute the average image from a list of images.

    :param images: List of images as numpy arrays
    :return: Average image as a numpy array
    """
    image_list = []
    
    
    output_average_image = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/" + year +'/'+ site + '_' + start_date + '_' + str(days_increment) + 'd_'

    #Parse the time span if provided
    if average_type == "specific":
        if start_time is None or end_time is None:
            raise ValueError("start_time and end_time must be provided for average_type 'specific'")
        start_time_datetime = datetime.strptime(start_time, "%Y-%m-%dT%H_%M_%S")
        end_time_datetime = datetime.strptime(end_time, "%Y-%m-%dT%H_%M_%S")
 
        output_average_image = output_average_image + average_type + '_' + start_time + '_' + end_time + '.tiff'  
        
    if average_type == "all":
        output_average_image = output_average_image + average_type +'.tiff'   
    
    
    
        # Read all TIFF images and store them in a list
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.tiff') or file_name.endswith('.tif'):
            # Extract the timestamp from the file name
            try:
                timestamp_str = file_name.split('_image')[0]
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H_%M_%S")
            except ValueError:
                # Skip files with invalid timestamps
                continue    
            # Check if the image falls within the specified time span
            if average_type == "all" or (start_time_datetime <= timestamp <= end_time_datetime):
                img_path = os.path.join(input_folder, file_name)
                image_data = tiff.imread(img_path)
                image_list.append(image_data)    
                
    print(len(image_list))     

            
    
    # Assuming all images are of the same shape
    sum_image = np.zeros_like(image_list[0], dtype=np.float64)
    
    for img in image_list:
        sum_image += img.astype(np.float64)
    
    average_image = sum_image / len(image_list)
    
    result_image = Image.fromarray(average_image)
    
    result_image.save(output_average_image)



def get_image_files_files(folder_path):
    """
    Get all the .tiff files in the specified folder.

    Parameters:
    folder_path (str): The path to the folder to search for .tiff files.

    Returns:
    list: A list of .tiff file names.
    """
    # List to store .tiff file names
    tiff_images = []

    # Iterate over all the files in the specified folder
    for file_name in os.listdir(folder_path):
        # Check if the file has a .tiff extension
        if file_name.lower().endswith('.tiff'):
            tiff_images.append(file_name)
    
    return tiff_images

#################################################################################################
############ ADD THE Geo INFO TO ANY FILE (the average at least) ###############################
################################################################################################

def extract_metadata(geotiff_path):
    with rasterio.open(geotiff_path) as src:
        metadata = src.meta.copy()
        return metadata['crs'], metadata['transform']

def add_georeferencing(untagged_tiff_path, crs, transform):
    with rasterio.open(untagged_tiff_path, 'r+') as dst:
        dst.crs = crs
        dst.transform = transform
        
        
def list_files_starting_with(folder_path, prefix):
    """
    Lists all files in a folder that start with a certain prefix.
    
    Args:
    - folder_path: Path to the folder.
    - prefix: Prefix to filter files.
    
    Returns:
    - List of file names starting with the specified prefix.
    """
    file_list = []
    for file_name in os.listdir(folder_path):
        if file_name.startswith(prefix):
            file_list.append(file_name)
    return file_list

#################################################################################################
######################## CREATE THE MOVIE ######################################################
################################################################################################

def create_movie_from_images(image_folder, output_movie, text1 , text2):
    #Text1 is the site's name 
    #Tes
    fps=3
    resize=None
    logging.basicConfig(level=logging.INFO)
    
    # Get the list of image files
    images = [img for img in os.listdir(image_folder) if img.endswith((".tiff", ".tif"))]
    if not images:
        logging.error("No images found in the specified folder.")
        return
    
    images.sort()  # Sort the images by name
    logging.info(f"Found {len(images)} images in the folder.")

    # Read the first image to get the dimensions
    first_image_path = os.path.join(image_folder, images[0])
    first_image = imageio.imread(first_image_path)
    
    # Determine if the images are grayscale or color
    if len(first_image.shape) == 2:  # Grayscale image
        height, width = first_image.shape
        is_color = False
    else:  # Color image
        height, width, layers = first_image.shape
        is_color = True

    # Optionally resize the images
    if resize:
        width, height = resize
        logging.info(f"Resizing images to {width}x{height}.")

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_movie, fourcc, fps, (width, height))

    for image_name in images:
        image_path = os.path.join(image_folder, image_name)
        image = imageio.imread(image_path)

        # Normalize the image to enhance visibility
        if image.dtype == np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        if not is_color:
            # Convert grayscale image to BGR (required by VideoWriter)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if resize:
            image = cv2.resize(image, (width, height))

        # Add text1 to the upper right part of the image
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.5
        font_color = (0, 255, 0)  # Green color, visible on both black and white backgrounds
        thickness = 1
        text1_size = cv2.getTextSize(text1, font, font_scale, thickness)[0]
        text1_x = width - text1_size[0] - 10
        text1_y = text1_size[1] + 10
        cv2.putText(image, text1, (text1_x, text1_y), font, font_scale, font_color, thickness)
        
        # Add text2 to the upper left part of the image
        text2_size = cv2.getTextSize(text2, font, font_scale, thickness)[0]
        text2_x = width - text2_size[0] - 10
        text2_y = text1_size[1] 
        cv2.putText(image, text2, (text2_x, text2_y), font, font_scale, font_color, thickness)
        
        # Add scale to the bottom left part of the image
        scale_start_x = 10
        scale_start_y = height - 20
        scale_length_10px = 50  # Length of 10 pixels
        scale_color = (0, 255, 0)  # Green color

        # Draw the 1200m scale
        cv2.line(image, (scale_start_x, scale_start_y), (scale_start_x + scale_length_10px, scale_start_y), scale_color, 5)
        cv2.putText(image, '3km', (scale_start_x + 10 , scale_start_y - 10), font, font_scale, scale_color, thickness)
        
        video.write(image)

    video.release()
    logging.info(f"Movie created successfully at {output_movie}")

    

################################################################################################################
########################## The different Parts of this code ##########################################################
################################################################################################################


# Part 1 refers to the computation of all the images of the A3 sites on the specified time period 

def Part1(formatted_dates, lat, rsize, res, lon, days_increment,type_illumination):   
    num_dates = len(formatted_dates)
    
    if type_illumination == 'S':
        source = 'SUN_MULTI'
    
    elif type_illumination == 'S+E':
        source = 'SUN_EARTH'
        
    
    for i in range(num_dates):
        print(formatted_dates[i])
        # Construct URL
        baseURL = 'https://qts.quickmap.io/fcgi-bin/fprovweb.exe?'
        url = (baseURL + 'source='+source
               + '&target=MOON'
               + '&utc_start=' + formatted_dates[i]
               + '&lat=' + str(lat)
               + '&lon=' + str(lon)
               + '&rsize=' + str(rsize)
               + '&res=' + str(res)
               + '&h_offset=2'
               + '&sdist=150'
               + '&_xtype=text/html&cmd_script=qts_js').replace(' ', '')
        
        # Initialize a Chrome webdriver (you can use other browsers too)
        driver = webdriver.Chrome()
        
        try:
            # Open the URL in the browser
            driver.get(url)
            
            # Wait for the submit button to be clickable and click it
            wait = WebDriverWait(driver, 10)  # Wait for a maximum of 10 seconds
            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn-id")))
            submit_button.click()
            
            # Wait for the pop-up window to appear and dismiss it
            popup_window = wait.until(EC.alert_is_present())
            popup_window.dismiss()
            
            # Find and click the button that triggers cb_run_qts() function
            buttons = driver.find_elements(By.XPATH, "//input[@value='Submit']")
            for button in buttons:
                onclick_value = button.get_attribute("onclick")
                if onclick_value and "cb_run_qts()" in onclick_value:
                    button.click()
                    break  # Exit the loop after clicking the button
            
            # Wait until the "(Beta) Simulation results" text appears
            while True:
                try:
                    element = driver.find_element(By.XPATH, "//*[contains(text(), '(Beta) Simulation results')]")
                    if element.is_displayed():
                        break
                except:
                    pass
                time.sleep(1)  # Wait for 1 second before checking again
            
            # Find and click on the hyperlink "Download Binary Shadow Mask as GeoTIFF"
            download_link = wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Download Binary Shadow Mask as GeoTIFF"))
            )

            # Wait for the href attribute to be updated with the actual download link
            while True:
                download_url = download_link.get_attribute("href")
                if download_url and not download_url.endswith("placeholder"):
                    break
                time.sleep(1)  # Wait for 1 second before checking again

            response = requests.get(download_url)
            if response.status_code == 200:
                if not os.path.exists(image_folder):
                    os.mkdir(image_folder)
                
                save_path = os.path.join(image_folder, formatted_dates_save[i] + '_image.tiff')
                with open(save_path, "wb") as f:
                    f.write(response.content)
                    print("Image saved successfully.")
            else:
                print("Failed to download the image.")
        except Exception as e:
            print("An error occurred:", str(e))
        finally:
            driver.quit()
            
            
def Part2(image_folder,year):

        
        #output_average_image = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/" + site + '_' + start_date + '_' + str(days_increment) + 'd.tiff'
        
            
        #os.makedirs("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/", exist_ok=True)
        #os.makedirs(output_average_image, exist_ok=True)
        
        
        #if os.path.exists(image_folder):
            
        # Average function a bit more advanced that would let the user to decide on which delta-t he wants to compute the average illumination map    
        #average_images(image_folder, average_type="all", start_time='2025-11-22T12_00_00', end_time='2025-11-24T12_00_00')
        
        average_images(image_folder,year, average_type = "all", start_time = '2025-11-20T00_00_00', end_time='2025-11-27T00_00_00')
        
        print('Averaged Image computed successfully')
        
        
def Part3(geotiff_path,files_list):
    
    for file_name in files_list:
        #untagged_tiff_path = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/"+file_name
        
        untagged_tiff_path = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/Temp_Files/"+file_name

        # Extract georeferencing information from GeoTIFF
        crs, transform = extract_metadata(geotiff_path)
        # Add georeferencing information to untagged TIFF
        add_georeferencing(untagged_tiff_path, crs, transform)
    
        print("Georeferencing added successfully.")
        
        
def Part4(image_folder,site,start_date,days_increment,short_date):
    
    year = formatted_dates_save[0][0:4]
    
    date_span = formatted_dates_save[0][0:4] + formatted_dates_save[0][4:10] +'/' + formatted_dates_save[-1][0:4] + formatted_dates_save[-1][4:10]
    
    output_movie = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Movies/"+year+ '/'+site +short_date + '_' + str(days_increment)+"d_movie.mp4"
    
    
    
    
    create_movie_from_images(image_folder, output_movie, site ,date_span)
    
def Part5(image_path,output_path_save,site,start_date,days_increment):
    
    # Load the image
    #image_path = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/ConnectingRidgeExtension_2025-11-20T00_00_00_32d_all.tiff'  # Replace with your actual image path
    image = Image.open(image_path)
    image_array = np.array(image)

    # Find the 5 maximum values' positions
    flat_image_array = image_array.flatten()
    indices = np.argpartition(flat_image_array, -5)[-5:]  # Get indices of the 5 largest values
    indices = indices[np.argsort(-flat_image_array[indices])]  # Sort the indices by the values
    positions = np.array(np.unravel_index(indices, image_array.shape)).T  # Convert flat indices to 2D positions
    values = flat_image_array[indices]*32  # Get the corresponding values

    # Plot the image with white triangles at the max positions
    plt.figure(figsize=(10, 10))
    plt.imshow(image_array, cmap='plasma')
    cbar = plt.colorbar()
    cbar.set_label('Days of Sunlight')
    cbar.set_ticks([0, 0.25,0.5 ,0.75,1])
    cbar.set_ticklabels(['0','8','16','24', '32'])
    plt.title(site+'_'+start_date+'_'+str(days_increment)+'d')
    for (y, x) in positions:
        plt.plot(x, y, marker='^', markersize=8, color='white', markeredgecolor='black', markeredgewidth=1.5)
        #plt.text(x, y, str(values[0]), color='black', fontsize=12, ha='center', va='center')
        
    # Add a single annotation with the max value in the upper right corner
    plt.text(0.95, 0.05, f'Max Value: {max(values)}', color='black', fontsize=15, ha='right', va='center', transform=plt.gca().transAxes)

    # Save and show the result
    #output_path = '/mnt/data/result_image_with_triangles.png'  # Replace with your desired output path
    plt.savefig(output_path_save)
    plt.show()
        

################################################################################################################
########################## WHAT NEEDS TO BE MODIFIED  ##########################################################
################################################################################################################

    
# SETUP THE START TIME + INCREMENT + TOTAL TIME EVALUATED
start_date = datetime(2036,5,21,00)  # Starting date - yyyy,mm,dd
hours_increment = 12  # Increment in hours
days_increment = 0 # Increment in days
num_dates = math.floor((24/hours_increment) * days_increment+1)     # Number of dates to generate

#Midsummer dates (ref:Mahanti et al) : 2025_11_20_32d / 2026_11_06_22d / 2027_10_15_31d / 2028_09_27_18d / 2029_10_02_18d

date_list = generate_date_list(start_date, hours_increment, days_increment, num_dates)  
# Format the list of dates
formatted_dates = format_date_list(date_list)
formatted_dates_save = format_date_list_save(date_list)

# SELECT TYPE OF ILLUMINATION SHADOW: 'S' or 'S+E' 
type_illumination = 'S' 

# GET THE IMPORTANT VALUE DEPENDING OF THE SITES 
file_path = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/QuickMap - perso codes/Center_coordinates_A3_regions.xlsx'
sites_data = pd.read_excel(file_path)


#len(sites_data.Name)
for j in range(11,12):
        site = sites_data.Name[j]
        print(site)
        
        lat = sites_data.center_latitude[j] # lat and long of the CENTER of the area to be mapped
        lon = sites_data.center_longitude[j]
        rsize = sites_data.region_size[j]
        res = sites_data.resolution[j]
        
        start_date = formatted_dates_save[0]
        short_date = formatted_dates_save[0][0:10]
        year = formatted_dates_save[0][0:4]
    
        if type_illumination == 'S':
            image_folder = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Sun Illumination/" + site + '/' + site + '_' + start_date + '_' + str(days_increment) + 'd/'
            
        elif type_illumination == 'S+E':
            image_folder = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Sun + Earth Illumination/"+ site + '/' + site + '_' + start_date + '_' + str(days_increment) + 'd/'

        
        #image_folder_2 = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/" + site + '_' + start_date + '_' + str(days_increment) + 'd'
        #output_average_image = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_images/"+ site + '_' + start_date + '_' + str(days_increment) + 'd.tiff'

        Part1(formatted_dates,lat,rsize,res,lon,days_increment,type_illumination) #Select type of illumination: 'S' for Sun only or 'S+E' for Sun AND Earth at the SAME time
        
        #Part2(image_folder,year)
        
        #geotiff_path = image_folder + formatted_dates_save[0] + '_image.tiff'
        #untagged_tiff_path = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/"+ site + '_' + formatted_dates_save[0] + '_' + str(days_increment) +'d.tiff'
        
        
        #average_image_folder = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/'
       # average_file_list = list_files_starting_with(average_image_folder, prefix = site + '_' + formatted_dates_save[0] )

        #Part3(geotiff_path,average_file_list)
        
        #Part4(image_folder,site,start_date,days_increment,short_date)
        
        #average_image = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images/'+site+ '_' + start_date + '_' + str(days_increment) + 'd_all.tiff'
        #output_path_save = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_Images_color/'+site+ '_' + start_date + '_' + str(days_increment) + 'd_all.tiff'
        
        #Part5(average_image,output_path_save,site,start_date,days_increment)
        
        
        
# site = sites_data.Name[0]
# print(site)

# lat = sites_data.center_latitude[0] # lat and long of the CENTER of the area to be mapped
# lon = sites_data.center_longitude[0]
# rsize = sites_data.region_size[0]
# res = sites_data.resolution[0]

# start_date = formatted_dates_save[0]

# image_folder = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/" + site + '_' + start_date + '_' + str(days_increment) + 'd/'
# #output_average_image = "/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/Average_images/"+ site + '_' + start_date + '_' + str(days_increment) + 'd.tiff'

# #Part1(formatted_dates,lat,rsize,res,lon,days_increment)

# #Part2()        



# crs, transform = extract_metadata(geotiff_path)
# # add_georeferencing(untagged_tiff_path, crs, transform)
# geotiff_path = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/QuickMap/deGerlacheRim2/deGerlacheRim2_2025-11-20T00_00_00_32d/2025-11-21T12_00_00_image.tiff'
# # untagged_tiff_path = '/Users/louis/Downloads/deGerlacheRim2_MaxConsecDaysOfSun_Midsummer2025GT.tif'
# # crs,transform = extract_metadata(geotiff_path)
# # add_georeferencing(untagged_tiff_path, crs, transform)
# folder_path = '/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Data & Images/Temp_Files'
# prefix = 'deGerlacheRim2'
# files_list = list_files_starting_with(folder_path, prefix)


# Part3(geotiff_path,files_list)
    

