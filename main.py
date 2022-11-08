import os
import cv2
import pathlib

def main():
    path = os.path.normcase(input("Enter the path to the pictures' directory: "))
    plate_num = int(input("Enter the plate number: "))
    drug_name = input("Enter the drug name: ")
    files = get_files_from_directory(path , '.png')

    output_dir = create_directory(path, f'ISO PL {plate_num} proccesed images')

    line_thickness = 2

    # Collect each group of 4 images after proccecing into an array by the order:
    # [0] : 24hr with drug - Will be the top left image in the final output
    # [1] : 24hr without drug - Will be the top right image in the final output
    # [2] : 48hr with drug - Will be the bottom left image in the final output
    # [3] : 48hr without drug - Will be the bottom right image in the final output
    picutres_1_to_4 = [None, None, None, None]
    picutres_5_to_8 = [None, None, None, None]
    picutres_9_to_12 = [None, None, None, None]

    # Crop the imges and lay the grid on them
    for picture in files:
        img = cv2.imread(picture)
        # Crop the image
        #start_row:end_row, start_col:end_col
        cropped_img = img[305:1615, 350:2255]
        
        pictue_name = pathlib.Path(picture).stem

        # lay the grid on the image
        # Top line
        cv2.line(cropped_img, (0, 130), (1800, 130), (0, 0, 0), line_thickness)
        row_ofsset = 134
        for i in range(0, 8):
            cv2.line(cropped_img, (0, 255 + (i*row_ofsset)), (1800, 255 + (i*row_ofsset)), (0, 0, 0), line_thickness)

        # Left line
        cv2.line(cropped_img, (125, 0), (125, 1300), (0, 0, 0), line_thickness)
        column_ofsset = 400
        for i in range(0, 4):
            cv2.line(cropped_img, (540 + (column_ofsset * i), 0), (540 + (column_ofsset * i), 1300), (0, 0, 0), line_thickness)

        # Add letters to the grid
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, letter in enumerate(letters):
            #Image, Start point: Top left, End point: Bottom right, Color, Thickness: -1 will fill the entire shape
            cv2.rectangle(cropped_img, (22, 153 + (i * row_ofsset)), (102, 233 + (i * row_ofsset)), (0, 0, 0), -1)
            # Add the letter to the rectangle
            cv2.putText(cropped_img, letter, (40, 214 + (i * row_ofsset)), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Add numbers to the grid
        if '1-4' in pictue_name:
            numbers = [1, 2, 3, 4]
        elif '5-8' in pictue_name:
            numbers = [5, 6, 7, 8]
        elif '9-12' in pictue_name:
            numbers = [9, 10, 11, 12]
        
        for i, number in enumerate(numbers):
            cv2.rectangle(cropped_img, (300 + (i * column_ofsset), 25), (380 + (i * column_ofsset) , 105), (0, 0, 0), -1)
            # Add the letter to the rectangle
            # If the number is larger than 9 then we need to move the number to the left a bit so it will be centered in the rectangle
            left_offset = -22 if number > 9 else 0
            cv2.putText(cropped_img, str(number), (320 + (i * column_ofsset) + left_offset, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Get the time from the picture name
        time = ''
        if '24hr' in pictue_name:
            time = '24hr'
        elif '48hr' in pictue_name:
            time = '48hr'

        # If the plate was a NO DRUG plate ND to name
        ND_text = ''
        if 'ND' in pictue_name:
            ND_text = 'ND'

        current_image_name = f'ISO PL {plate_num} {drug_name} {time} {numbers[0]}-{numbers[-1]} {ND_text}.png'
        cv2.imwrite(os.path.join(output_dir, current_image_name), cropped_img)

        # Add the image to the correct array
        if '1-4' in pictue_name:
            picutres_1_to_4[get_image_index(current_image_name)] = cropped_img
        elif '5-8' in pictue_name:
            picutres_5_to_8[get_image_index(current_image_name)] = cropped_img
        elif '9-12' in pictue_name:
            picutres_9_to_12[get_image_index(current_image_name)] = cropped_img
            
    # Check that all the arrays have 4 images in them and not the None values assigned to them as indication that the image is missing.
    # No None values should be in the arrays
    assert any(list(item is not None for item in picutres_1_to_4))
    assert any(list(item is not None for item in picutres_5_to_8))
    assert any(list(item is not None for item in picutres_9_to_12))

    joined_picutres_1_to_4 = make_four_picture_grid(picutres_1_to_4[0], picutres_1_to_4[1], picutres_1_to_4[2], picutres_1_to_4[3])
    cv2.imwrite(os.path.join(output_dir, f'ISO PL {plate_num} {drug_name} 1-4 Combined image.png'), joined_picutres_1_to_4)

    joined_picutres_5_to_8 = make_four_picture_grid(picutres_5_to_8[0], picutres_5_to_8[1], picutres_5_to_8[2], picutres_5_to_8[3])
    cv2.imwrite(os.path.join(output_dir, f'ISO PL {plate_num} {drug_name} 5-8 Combined image.png'), joined_picutres_5_to_8)

    joined_picutres_9_to_12 = make_four_picture_grid(picutres_9_to_12[0], picutres_9_to_12[1], picutres_9_to_12[2], picutres_9_to_12[3])
    cv2.imwrite(os.path.join(output_dir, f'ISO PL {plate_num} {drug_name} 9-12 Combined image.png'), joined_picutres_9_to_12)
        

def get_files_from_directory(path , extension):
    '''Get the full path to each file with the extension specified from the path'''
    files = []
    for file in os.listdir(path):
        if file.endswith(extension):
            files.append(os.path.join(path ,file))
    return files

def create_directory(father_directory, nested_directory_name):
    '''
    Description
    -----------
    Create a directory if it does not exist
    
    Parameters
    ----------
    father_directory : str
        The path to the directory under which the new directory will be created
    nested_directory_name : str
        The name of the nested directory to be created
    '''
    # Create the output directory path
    new_dir_path = os.path.join(father_directory, nested_directory_name)
    # Create the directory if it does not exist
    if not os.path.isdir(new_dir_path):
        os.mkdir(new_dir_path)
    return new_dir_path

def make_four_picture_grid(top_left, top_right, bottom_left, bottom_right):
    '''Join 4 images into one image'''
    # Join the images into one image
    top = cv2.hconcat([top_left, top_right])
    bottom = cv2.hconcat([bottom_left, bottom_right])
    joined_picutres = cv2.vconcat([top, bottom])
    return joined_picutres

def get_image_index(image_name):
    '''Get the index of the image should be inserted into the array'''
    # If the image has no drug strips then it's the second image in the row
    is_ND = 'ND' in image_name
    if '24hr' in image_name:
        if not is_ND:
            return 0
        else:
            return 1
    elif '48hr' in image_name:
        if not is_ND:
            return 2
        else:
            return 3

if __name__ == '__main__':
    main()