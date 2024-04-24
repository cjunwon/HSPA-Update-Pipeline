import io
import json
import time

import requests
from bs4 import BeautifulSoup
import boto3
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import KDTree

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

import tensorflow as tf
from tensorflow import keras

from pykrige.ok import OrdinaryKriging


url_data_la_city = 'https://data.lacity.org/api/geospatial/yjxu-2kqq?method=export&format=GeoJSON'

s3_bucket = 'srilabgeodata'
s3_key_main_db = 'hillside_inventory_LA_centrality_full_new_evacmidnorth.geojson'
s3_key_street_centerline = 'Streets_Centerline_For_URL.geojson'

s3 = boto3.client('s3')
obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
df = gpd.read_file(io.BytesIO(obj['Body'].read()))

# Extract features (latitude and longitude) and target (PCI)
lats = np.array(df["centroid_lat"]).reshape((-1, 1))
lons = np.array(df["centroid_lon"]).reshape((-1, 1))
pci = np.array(df["pci"])

# Combine latitude and longitude into features
features = np.concatenate([lats, lons], axis=1)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(features, pci, test_size=0.3, random_state=42)

def linear_regression():
    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print_result("Linear Regression", predictions)

def random_forest_regression():

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print_result("Random Forest Regression", predictions)   

def k_nearest_neighbor():

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    knn_model = KNeighborsRegressor(n_neighbors=2)  #we can adjust k here

    knn_model.fit(X_train_scaled, y_train)

    knn_predictions = knn_model.predict(X_test_scaled)
    print_result("K-Nearest Neighbor", knn_predictions)


def neural_network():

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Define the neural network architecture
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1)  # Output layer with one neuron for regression
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X_train_scaled, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

    nn_predictions = model.predict(X_test_scaled).flatten()

    print_result("Neural Network", nn_predictions)

def interpolation():
    centroids = np.concatenate([lats, lons], axis=1)
    kdpoints = KDTree(centroids)

    pcis_prefinal = np.array(df["pci"])
    pcis_prefinal_new = np.array(df["pci"])

    kmax = 0

    # Predict for X_test
    predictions = []
    for i in range(len(X_test)):
        point = centroids[len(X_train) + i, :]
        k = 5
        while True:
            result = kdpoints.query(point, k=k)

            dsts = result[0][1:]
            idxs = result[1][1:]
            pcis = pcis_prefinal[list(idxs)]
            dsts_new = dsts[pcis != -1.0]
            idxs_new = idxs[pcis != -1.0]
            pcis_new = pcis[pcis != -1.0]
            if len(pcis_new) > 2:
                if k > kmax:
                    kmax = k
                break
            else:
                k += 1
        dstsum = sum(1 / dsts_new)

        pcinew = sum(pcis_new * (1 / dsts_new)) / dstsum
        predictions.append(pcinew)
    print_result("Missing_points", predictions)

def print_result(name, predictions):
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, predictions)

    print()
    print(name)
    print("Mean Absolute Error (MAE):", mae)
    print("Mean Squared Error (MSE):", mse)
    print("Root Mean Squared Error (RMSE):", rmse)
    print("R^2 Score:", r2)
    print()

    count10 = 0
    count20 = 0

    for pred, actual in zip(predictions, y_test):
        if abs(actual - pred) < 10:
            count10 += 1
            count20 += 1
        elif abs(actual - pred) < 20:
            count20 += 1 
    print("There are " + str(count10) + " <10 diff results" + " out of " + str(len(predictions)))
    print("There are " + str(count20) + " <20 diff results" + " out of " + str(len(predictions)))

    #     print("{:.2f}\t\t{:.2f}".format(pred, actual))
    # print()

neural_network()
linear_regression()
random_forest_regression()
k_nearest_neighbor()
interpolation()


