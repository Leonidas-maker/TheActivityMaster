from fastapi import  UploadFile
import uuid
from typing import List
import os

from config import settings

def write_identification_verification(user_id: uuid.UUID, image_files: List[UploadFile]) -> str:
    """
    Write the identification verification of a user

    :param user_id: The user id
    :param image_files: The image files
    :return: The path to the verification
    """
    
    os.makedirs(settings.VERIFICATION_ID_PATH, exist_ok=True)
    image_path = settings.VERIFICATION_ID_PATH / str(user_id)


    if os.path.exists(image_path):
        raise FileExistsError("User already has an identification verification")
    
    os.makedirs(image_path, exist_ok=True)

    for image_file in image_files:
        if not image_file.filename: 
            raise ValueError("Image file name is required")
        with open(image_path / image_file.filename, "wb") as image:
            image.write(image_file.file.read())

    return str(image_path)

def clear_identification_verification(user_id: uuid.UUID, throw_error: bool = True) -> None:
    """
    Clear the identification verification of a user

    :param user_id: The user id
    """
    image_path = settings.VERIFICATION_ID_PATH / str(user_id)

    if  not os.path.exists(image_path):
        if throw_error:
            raise FileNotFoundError("User does not have an identification verification")
        return

    for image_file in os.listdir(image_path):
        os.remove(image_path / image_file)

    os.rmdir(image_path)