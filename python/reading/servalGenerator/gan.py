from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, Activation, Reshape
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import UpSampling2D
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers import Flatten, Dropout
import math
import numpy as np
import os
from keras.datasets import mnist
from keras.optimizers import Adam
import FriendsLoader
import cv2

IMG_SIZE = 100
BATCH_SIZE = 100
NUM_EPOCH = 1000
GENERATED_IMAGE_PATH = "tmp/" # 生成画像の保存先

def generator_model():
    layerSize = int(IMG_SIZE/4)
    model = Sequential()
    model.add(Dense(2048, input_shape=(IMG_SIZE,)))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Dense(layerSize*layerSize*256))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Reshape((layerSize, layerSize, 256)))
    model.add(UpSampling2D((2, 2)))
    model.add(Conv2D(128, (5, 5), padding="same"))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(UpSampling2D((2, 2)))
    model.add(Conv2D(3, (5, 5), padding="same"))
    model.add(Activation("tanh"))
    return model

def discriminator_model():
    model = Sequential()
    model.add(Conv2D(128, (5, 5),
                    strides=(2, 2),
                    padding='same',
                    input_shape=(IMG_SIZE, IMG_SIZE, 3))) # ここ注意
    model.add(LeakyReLU(0.2))
    model.add(Conv2D(256, (5, 5), strides=(2, 2)))
    model.add(LeakyReLU(0.2))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(LeakyReLU(0.2))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation("sigmoid"))
    return model

def combine_images(generated_images):

    # メモ : この時点で generated_images.shape = (32, 28, 28, 1) のはず

    total = generated_images.shape[0]
    cols = int(math.sqrt(total))
    rows = math.ceil(float(total)/cols)
    width, height = generated_images.shape[1:3]
    combined_image = np.zeros((height*rows, width*cols, 3),dtype=generated_images.dtype)

    for index, image in enumerate(generated_images):
        i = int(index/cols)
        j = index % cols
        for k in range(3):
            combined_image[width*i:width*(i+1), height*j:height*(j+1), k] = image[:, :, k]
    return combined_image

def train():
    # (X_train, y_train), (_, _) = mnist.load_data()
    (X_train, y_train), (_, _) = FriendsLoader.load_data()
    X_train = (X_train.astype(np.float32) - 127.5)/127.5
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 3)

    # メモ : X_train.shape = (60000, 28, 28, 1)

    if os.path.exists("discriminator.json"):
        with open("discriminator.json", "r", encoding="utf-8") as f:
            discriminator = model_from_json(f.read())
    else:
        discriminator = discriminator_model()
    d_opt = Adam(lr=1e-5, beta_1=0.1)
    if os.path.exists("discriminator.h5"):
        discriminator.load_weights("discriminator.h5", by_name=False)
    discriminator.compile(loss="binary_crossentropy", optimizer=d_opt)
    with open("discriminator.json", "w", encoding="utf-8") as f:
        f.write(discriminator.to_json())
    discriminator.summary()

    # generator+discriminator （discriminator部分の重みは固定）
    discriminator.trainable = False
    if os.path.exists("generator.json"):
        with open("generator.json", "r", encoding="utf-8") as f:
            generator = model_from_json(f.read())
    else:
        generator = generator_model()
    dcgan = Sequential([generator, discriminator])
    g_opt = Adam(lr=2e-4, beta_1=0.5)
    if os.path.exists("generator.h5"):
        generator.load_weights("generator.h5", by_name=False)
    dcgan.compile(loss="binary_crossentropy", optimizer=g_opt)
    with open("generator.json", "w", encoding="utf-8") as f:
        f.write(generator.to_json())
    num_batches = int(X_train.shape[0] / BATCH_SIZE)
    print("Number of batches:", num_batches)
    for epoch in range(NUM_EPOCH):

        for index in range(num_batches):
            noise = np.array([np.random.uniform(-1, 1, IMG_SIZE) for _ in range(BATCH_SIZE)])
            
            # メモ : noise.shape = (32(バッチサイズ), 100)

            image_batch = X_train[index*BATCH_SIZE:(index+1)*BATCH_SIZE]
            generated_images = generator.predict(noise, verbose=0)

            # 生成画像を出力
            if index % 50 == 0:
                image = combine_images(generated_images)
                image = image*127.5 + 127.5
                if not os.path.exists(GENERATED_IMAGE_PATH):
                    os.mkdir(GENERATED_IMAGE_PATH)
                cv2.imwrite(GENERATED_IMAGE_PATH+"%04d_%04d.png" % (epoch, index), image.astype(np.uint8))

            # discriminatorを更新
            X = np.concatenate((image_batch, generated_images))
            y = [1]*BATCH_SIZE + [0]*BATCH_SIZE
            d_loss = discriminator.train_on_batch(X, y)

            # generatorを更新
            noise = np.array([np.random.uniform(-1, 1, IMG_SIZE) for _ in range(BATCH_SIZE)])
            g_loss = dcgan.train_on_batch(noise, [1]*BATCH_SIZE)
            print("epoch: %d, batch: %d, g_loss: %f, d_loss: %f" % (epoch, index, g_loss, d_loss))

        generator.save_weights("generator.h5")
        discriminator.save_weights("discriminator.h5")

if __name__ == "__main__":
    train()
