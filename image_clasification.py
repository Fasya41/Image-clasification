# -*- coding: utf-8 -*-
"""sampel IDCamp-Image-Clasification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SuYdvw94rav1eyu3VstwyrS800ARqh5e

#PREPARITION AND EXPLORE DATA

##Instal Kagle and Download Dataset from Kagle
"""

!pip install kaggle

!mkdir ~/.kaggle #create the directory with the name kagle

!cp kaggle.json ~/.kaggle # Copy the Kagle API file ito the directory that has been created

!chmod 600 ~/.kaggle/kaggle.json #grant file acces permissions

!kaggle datasets list

!kaggle datasets download -d 'khnhtrng/flowers' #Download Dataset From Kaggle

"""## Import Library"""

# For processing data
import os
import zipfile
import pathlib
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from tqdm import tqdm
import cv2
import numpy as np
import random as rn
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.models import Sequential

# For visualization
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
plt.style.use('ggplot')

"""## Explore the Data"""

#Extract the downloaded zip file
local_zip = '/content/flowers.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

os.listdir('/content/flowers') #Check inside the directory

#check the amount of data for each folder
for label in os.listdir('/content/flowers'):
  print(f'Total {label} images :', len(os.listdir(f'/content/flowers/{label}')))

#visualization Image
img = image.load_img('/content/flowers/sunflower/10541580714_ff6b171abd_n.jpg')
imgplot = plt.imshow(img)

def assign_label(img,flower_type):
    return flower_type

def make_train_data(flower_type,DIR):
    for img in tqdm(os.listdir(DIR)):
        label=assign_label(img,flower_type)
        path = os.path.join(DIR,img)
        img = cv2.imread(path,cv2.IMREAD_COLOR)
        img = cv2.resize(img, (IMG_SIZE,IMG_SIZE))

        X.append(np.array(img))
        Z.append(str(label))

"""#NORMALIZATION AND SPLIT DATA

##preparation for augmentation
"""

#create the variabel
X=[]
Z=[]
IMG_SIZE=150
#create the variabel for path the folder
FLOWER_DAISY_DIR='/content/flowers/daisy'
FLOWER_SUNFLOWER_DIR='/content/flowers/sunflower'
FLOWER_TULIP_DIR='/content/flowers/tulip'
FLOWER_DANDI_DIR='/content/flowers/dandelion'
FLOWER_ROSE_DIR='/content/flowers/rose'

#change the image to array numpy
make_train_data('daisy',FLOWER_DAISY_DIR)
print(len(X))

make_train_data('sunflower',FLOWER_SUNFLOWER_DIR)
print(len(X))

make_train_data('sunflower',FLOWER_TULIP_DIR)
print(len(X))

make_train_data('sunflower',FLOWER_DANDI_DIR)
print(len(X))

make_train_data('sunflower',FLOWER_ROSE_DIR)
print(len(X))

"""##Nomalization Data"""

le=LabelEncoder()#maximize labels
#converts a class vector to binary class matrix
Y=le.fit_transform(Z)
Y=to_categorical(Y,5)
#Normalization Data
X=np.array(X)
X=X/255

"""##Split data Train and Validation"""

#Split data train 80% and data validation 20% from total data
x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=42)

np.random.seed(42)
rn.seed(42)
tf.random.set_seed(42)

"""#MODELLING AND AUGMENTATION

#Modelling
"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (5,5), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2,2)),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Conv2D(80, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2,2)),
    tf.keras.layers.Conv2D(96, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2,2)),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax')
])

"""##Augmentation"""

datagen = ImageDataGenerator(
        featurewise_center=False,
        samplewise_center=False,
        featurewise_std_normalization=False,
        samplewise_std_normalization=False,
        zca_whitening=False,
        rotation_range=10,
        zoom_range = 0.1,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=False)


datagen.fit(x_train)

"""#PREPARATION AND TRAINING MODEL

##Create the Callback
"""

batch_size=128
epochs=20

callback_cp = tf.keras.callbacks.ModelCheckpoint(
    filepath="/content/nice-val/val-improvement-{epoch:02d}-{val_accuracy:.2f}.hdf5",
    monitor="val_accuracy",
    verbose=1,
    save_best_only=True,
    mode="max"
)

from keras.callbacks import ReduceLROnPlateau
red_lr= ReduceLROnPlateau(monitor='val_acc',patience=3,verbose=1,factor=0.1)

"""##Model Summary"""

model.compile(optimizer=tf.optimizers.Adam(learning_rate=0.001),loss='categorical_crossentropy',metrics=['accuracy'])

model.summary()

"""#Training MODEL"""

History = model.fit(datagen.flow(x_train,y_train, batch_size=batch_size),
                              epochs = epochs, validation_data = (x_test,y_test),
                              verbose = 1, steps_per_epoch=x_train.shape[0] // batch_size, callbacks=[callback_cp])

"""#Vizualiatation And Check Result Model

Cizualitation Loss and Accuracy
"""

import matplotlib.pyplot as plt

acc = History.history['accuracy']
val_acc = History.history['val_accuracy']
loss = History.history['loss']
val_loss = History.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'r', label='accuracy Training ')
plt.plot(epochs, val_acc, 'b', label='accuracy Validasi')
plt.title('accuracy Training and Validasi')
plt.legend(loc=0)
plt.figure()
plt.show()

plt.plot(epochs, loss, 'r', label='loss Training ')
plt.plot(epochs, val_loss, 'b', label='loss Validasi')
plt.title('loss Training and Validasi')
plt.legend(loc=0)
plt.figure()
plt.show()

"""#SAVE THE MODEL INTO TF-LITE FORMAT"""

from keras.models import load_model
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score

pred=model.predict(x_test)
pred=(pred>0.01) .astype (int)
y_true=np.reshape (y_test, [-1])
y_pred=np.reshape (pred, [-1])
#Evaluation index
accuracy=accuracy_score (y_true, y_pred)
precision=precision_score (y_true, y_pred)
recall=recall_score (y_true, y_pred, average="binary")
f1score=f1_score (y_true, y_pred, average="binary")
print ("accuracy:", accuracy)
print ("precision:", precision)
print ("recall:", recall)
print ("f1score:", f1score)

# Save the model with SavedModel format
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

# Convert SavedModel to vegs.tflite
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('flowes.tflite')
tflite_model_file.write_bytes(tflite_model)

tflite_model_size = len(tflite_model) / (1024 * 1024)
print('TFLite model size = %d MBs.' % tflite_model_size)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_quantdefault_model = converter.convert()

os.mkdir("/content/model-tflite-quantdefault")
f = open('/content/model-tflite-quantdefault/model.tflite', "wb")
f.write(tflite_quantdefault_model)
f.close()

size_tflite_quantdefault = len(tflite_quantdefault_model) / (1024 * 1024)
print('TFLite quant model size = %d MBs.' % size_tflite_quantdefault)
print(f"Decreased : {(tflite_model_size - size_tflite_quantdefault) / tflite_model_size * 100} %")