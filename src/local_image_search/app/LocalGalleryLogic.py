from simplegallery.logic.base_gallery_logic import BaseGalleryLogic
import glob
import os
import simplegallery.common as spg_common
import simplegallery.media as spg_media
import json
from simplegallery.media import get_image_date, get_image_description, get_image_size, get_video_size
from typing import List
from pathlib import Path, PurePath


THUMBNAIL_SIZE_FACTOR = 2
THUMBNAIL_HEIGHT = 200
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def create_thumbnails(image_paths:List[Path], thumbnails_path:Path,force=False):
    """
    Checks if every image has an existing thumbnail and generates it if not (or if forced by the user)
    :param force: Forces generation of thumbnails if set to true
    """

    # Multiply the thumbnail size by the factor to generate larger thumbnails to improve quality on retina displays
    thumbnail_height = (
        THUMBNAIL_HEIGHT
        * THUMBNAIL_SIZE_FACTOR
    )

    count_thumbnails_created = 0
    
    thumbnail_dict = {}

    for image_path in image_paths:
        
        thumbnail_path = generate_thumbnail(thumbnails_path, image_path, thumbnail_height, force)
        if thumbnail_path:
            thumbnail_dict[image_path] = thumbnail_path
            count_thumbnails_created += 1
        
    spg_common.log(f"New thumbnails generated: {count_thumbnails_created}")
    return count_thumbnails_created


def generate_thumbnail(thumbnails_path:Path, image_path:Path, thumbnail_height:int, force=False):
    try:
        # Check if the thumbnail should be generated. This happens if one of the following applies:
        # - Forced by the user with -f
        # - No thumbnail for this image
        # - The thumbnail image size doesn't correspond to the specified size
        thumbnail_path = get_thumbnail_name(thumbnails_path, image_path)
        if (
            force
            or not os.path.exists(thumbnail_path)
            or not check_correct_thumbnail_size(thumbnail_path, thumbnail_height)
        ):
            spg_media.create_thumbnail(str(image_path), str(thumbnail_path), thumbnail_height)
            return thumbnail_path
    except FileNotFoundError:
        spg_common.log(f"Thumbnail for {image_path} could not be generated")
    return None


def format_image_date(timestamp):
    """
    Formats an image date according to the format specified in the gallery config.
    If no format is specified an empty string is returned
    :param timestamp: datetime object
    :return: Image date string or an empty string
    """
    image_date_string = ""

    try:
        image_date_string = timestamp.strftime(
            DATE_FORMAT
        )
    except ValueError:
        pass

    return image_date_string

def generate_images_data(images_path,thumbnails_path):
    """
    Generates the metadata of each image file
    :param images_data: Images data dictionary containing the existing metadata of the images and which will be
    updated by this function
    :return updated images data dictionary
    """

 
    images_data = {}
    # Get the required metadata for each image
    for image in images_path:
        image_data = generate_image_data(image, thumbnails_path)
        images_data[image_data["src"]] = image_data


    return images_data

def generate_image_data(image_path, thumbnails_path):
    """
    Generates the metadata of an image file
    :param image_path: Path to the image file
    :return: Dictionary containing the metadata of the image
    """
    try:

        thumbnail_path = get_thumbnail_name(
            thumbnails_path, image_path
        )
        image_data = get_metadata(
            image_path, thumbnail_path
        )

        # Scale down the thumbnail size to the display size
        image_data["thumbnail_size"] = (
            round(
                image_data["thumbnail_size"][0]
                / THUMBNAIL_SIZE_FACTOR
            ),
            round(
                image_data["thumbnail_size"][1]
                / THUMBNAIL_SIZE_FACTOR
            ),
        )

        # Format the image date
        image_data["date"] = format_image_date(image_data["date"])

        # If the date is filled, set the description to a non-empty string so it is shown
        if image_data["date"] and not image_data["description"]:
            image_data["description"] = " "
        
        return image_data

    except FileNotFoundError:
        spg_common.log(f"Metadata for {image_path} could not be generated")

    


def create_images_data_file(image_paths:List[Path], thumbnails_path:Path, path_to_images_data_file:Path):
    """
    Creates or updates the images_data.json file with metadata for each image (e.g. size, description and thumbnail)
    """

    images_data = generate_images_data(image_paths,thumbnails_path)

    # Write the data to the JSON file
    with open(path_to_images_data_file, "w", encoding="windows-1250") as images_out:
        json.dump(images_data, images_out, indent=4, separators=(",", ": "))

def check_correct_thumbnail_size(thumbnail_path, expected_height):
    """
    Check if a thumbnail has the correct height
    :param thumbnail_path: Path to the thumbnail file
    :param expected_height: Expected height of the thumbnail in pixels
    :return: True if the height of the thumbnail equals the expected height, False otherwise
    """
    return expected_height == spg_media.get_image_size(thumbnail_path)[1]

def get_thumbnail_name(thumbnails_path:Path, image_path:Path):
    """
    Generates the path to the thumbnail of an image
    :param thumbnails_path: Path to the folder containing the thumbnails
    :param image_path: Path to the image
    :return: Path to the thumbnail of the image
    """
    
    return thumbnails_path / image_path.name


def get_metadata(image:Path, thumbnail_path:Path):
    """
    Gets the metadata of a media file (image or video)
    :param image: Path to the media file
    :param thumbnail_path: Path to the thumbnail image of the media file
    :param public_path: Path to the public folder of the gallery
    :return:
    """
    # Paths should be relative to the public folder, because they will directly be used in the HTML
    image_data = dict(
        src=str(image.absolute()),
        mtime=os.path.getmtime(image),
        date=get_image_date(str(image)),
    )

    if image.suffix.endswith("jpg") or image.suffix.endswith(".jpeg"):
        image_data["size"] = get_image_size(image)
        image_data["type"] = "image"
        image_data["description"] = get_image_description(image)
    elif image.suffix.endswith(".gif") or image.suffix.endswith(".png"):
        image_data["size"] = get_image_size(image)
        image_data["type"] = "image"
        image_data["description"] = ""
    elif image.suffix.endswith(".mp4"):
        image_data["size"] = get_video_size(image)
        image_data["type"] = "video"
        image_data["description"] = ""
        thumbnail_path = thumbnail_path.replace(".mp4", ".jpg")
    else:
        raise spg_common.SPGException(
            f"Unsupported file type {image.name}"
        )

    image_data["thumbnail"] = str(thumbnail_path.absolute())
    image_data["thumbnail_size"] = get_image_size(thumbnail_path)

    return image_data


def get_all_image_paths(path):
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                yield Path(root, filename)

import sqlite3
def export_to_sql(images_data_path:Path,db_path:Path):

    # src, mtime, date, type, thumbnail, description
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    # if table doesn't exist, create it
    if not c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images';").fetchone():
        c.execute('''CREATE TABLE images
                        (src text, mtime real, date text, type text, thumbnail text, description text)''')
    
    with open(images_data_path, "r", encoding="windows-1250") as images_in:
        images_data = json.load(images_in)
        for image in images_data.values():
            if not c.execute("SELECT * FROM images WHERE src=?",(image["src"],)).fetchone():
                c.execute("INSERT INTO images VALUES (?,?,?,?,?,?)", (image["src"], image["mtime"], image["date"], image["type"], image["thumbnail"], image["description"]))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    image_paths = list(get_all_image_paths("./images"))
    thumbnails_path = Path("./thumbnails")
    create_thumbnails(image_paths, thumbnails_path)
    images_data_path = Path("./images_data.json")
    create_images_data_file(image_paths, thumbnails_path, images_data_path)
    db_path = Path("./images.db")
    export_to_sql(images_data_path, db_path)
