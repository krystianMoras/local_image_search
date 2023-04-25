import pandas as pd
import cv2
import yaml

cfg = yaml.safe_load(open("config.yaml"))


def get_colors(face_pointer,people,names):
    colors = ["gray" for i in range(len(names))]
    print(people)
    if face_pointer in people.face_id:
        # get name of person from people, face_id is an index
        name = people.loc[face_pointer, "name"]
        # get index of name in names
        index = list(names).index(name)
        colors[index] = "lime"


    return [colors]



def get_face_image(face_id,faces):
    face = faces.iloc[face_id]
    x, y, w, h = face["x"], face["y"], face["w"], face["h"]
    image_path = "images" + "/" + face["image_id"]
    # load image in lower resolution
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 20)
    return img




def read_people_csv(numb_of_faces):
    # read people.csv, if it doesn't exist, create it
    try:
        people = pd.read_csv(cfg["faces_names"])
    except FileNotFoundError:
        #populate with "unknown"
        people_list = []
        for i in range(numb_of_faces):
            people_list.append({"name": "nieznajomy", "face_id": i})
        people = pd.DataFrame(people_list, columns=["name", "face_id"])
        
        people.to_csv(cfg["faces_names"], index=False)
    return people