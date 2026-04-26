from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
import os

def train_collaborative_filtering():
    print("Initializing Spark Session...")
    spark = SparkSession.builder \
        .appName("MusicRecommender") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
    
    # Mocking a dataset for demonstration. 
    # In reality, this would be your Million Song Dataset interaction logs.
    print("Loading data...")
    data = [
        (1, 101, 5.0), (1, 102, 3.0), (1, 103, 1.0),
        (2, 101, 4.0), (2, 104, 5.0), (2, 105, 2.0),
        (3, 102, 4.0), (3, 103, 5.0), (3, 106, 4.0)
    ]
    df = spark.createDataFrame(data, ["user_id", "track_id", "play_count"])
    
    print("Training ALS Model...")
    als = ALS(
        maxIter=10, 
        regParam=0.1, 
        userCol="user_id", 
        itemCol="track_id", 
        ratingCol="play_count", 
        coldStartStrategy="drop"
    )
    model = als.fit(df)
    
    # Save the model
    model_path = "models/als_model"
    if not os.path.exists(model_path):
        model.save(model_path)
        print(f"Model saved successfully to {model_path}")
    else:
        print("Model directory already exists. Skipping save to prevent overwrite.")
        
    spark.stop()

if __name__ == "__main__":
    train_collaborative_filtering()