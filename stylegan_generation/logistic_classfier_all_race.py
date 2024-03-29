# -*- coding: utf-8 -*-
"""Logistic-Classfier-All race

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NgE4BKBMN1xG8K9AbnwG99yIrNFSMjnN
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True, help="Path to dataset")
    parser.add_argument("-e", "--exp_dir", required=True,
                        help="Path to race classifier model. It should contain checkpoint.h5 file")
    args = parser.parse_args()
    return args

def load_dataset(args, race):
    path = args.path
    race_path = os.path.join(path, race)
    positive_paths = []
    
    for p in os.listdir(race_path):
          if os.path.exists(os.path.join(race_path, p, "latents.csv")):
              positive_paths.append(os.path.join(race_path, p))
    other_races = set(os.listdir(path))
    other_races.remove(race)

    negative_paths = []
    for r in other_races:
        for p in os.listdir(os.path.join(path, r)):
              if os.path.exists(os.path.join(path, r, p, "latents.csv")):
                  negative_paths.append(os.path.join(path, r, p))
    negative_paths = np.random.choice(negative_paths, len(positive_paths)).tolist()
    all_paths = positive_paths + negative_paths
    latent_inputs = []
    latent_inputs_labels = []
    for i in range(len(all_paths)):
        current_path = all_paths[i]
        current_label = i < len(positive_paths)
        current_latents = pd.read_csv(os.path.join(current_path, "latents.csv")).numpy().tolist()
        latent_inputs += current_latents
        latent_inputs_labels += [current_label] * len(current_latents)

    latent_inputs = np.array(latent_inputs)
    latent_inputs_labels = np.array(latent_inputs_labels)

    shuffle_index = np.arange(len(latent_inputs))
    np.random.shuffle(shuffle_index)
    latent_inputs = latent_inputs[shuffle_index]
    latent_inputs_labels = latent_inputs_labels[shuffle_index]
    print("Latents inputs", latent_inputs.shape)
    print("latent_inputs_labels", latent_inputs_labels.shape)
    return latent_inputs, latent_inputs_labels
        
    
          
def classify_latent_space(race, args):

  X, y  = load_dataset(args, race)
  x_train, x_test, labels_train, labels_test = train_test_split(X,y, test_size=0.3)
  
  y_train = (labels_train==race).astype(np.float32)
  y_test = (labels_test==race).astype(np.float32)
  print("Traing for: {} race".format(race))
  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(512,)),
    tf.keras.layers.Dense(1, activation="sigmoid")
  ])
  model.compile(
      loss='binary_crossentropy',
      optimizer=tf.keras.optimizers.Adam(0.001),
      metrics=['accuracy']
  )
  model.fit(
      x_train, 
      y_train,
      epochs=100,
      validation_data=(x_test, y_test),
      class_weight={0: 0.4, 1: 0.6}
  )
  
  if not os.path.exists(args.exp_dir):
        os.mkdir(args.exp_dir)
  weights, bias = model.get_weights()
  np.save(os.path.join(args.exp_dir, "{}-race-direction-weights.npy".format(race)), weights)
  print("Completed training logistic classifier for {} race".format(race))


def main(args):
    races = os.listdir(args.path)
    for race in races:
      classify_latent_space(race, args)
   

if __name__ == '__main__':
    args = get_args()
    main(args)
    

