# local_image_search

Currently, to perform image search on your files, you need to upload it to a cloud service provider. This is not necessary, a lot of models can be run on local machines. Using vector storage allows to reduce computation to just few runs per image. Even for few hundred GB of data, this is not a problem, run it in background.

THe goal of this project is to enable basic image search capabilities (face search, landmarks) on local machines without a need to upload all your data. User interface should be basic and understandable for average Joe.

Plug in your hard disk -> Select folder -> (wait a few hours) -> classify a few faces -> vector store and sql database will be saved next to your data 

Another month, there are new images and videos -> identify diff, append embeddings

Search and view images in few clicks, aesthetically pleasing gallery


### Libraries

https://github.com/haltakov/simple-photo-gallery
https://github.com/serengil/deepface


