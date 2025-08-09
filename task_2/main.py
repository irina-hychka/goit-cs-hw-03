from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Local MongoDB connection string for Docker container
# Using the credentials from your docker-compose.yml
MONGO_URI = "mongodb://root:example@localhost:27017/"

try:
    # Connect to MongoDB
    mongo_client = MongoClient(MONGO_URI)

    # Check connection with a simple command
    mongo_client.admin.command("ping")
    print("Successfully connected to MongoDB.")

    # Select database and collection
    cats_database = mongo_client.cats_db
    cats_collection = cats_database.cats

except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit()


def create_doc(name, age, features):
    """
    Create a new cat document.

    Args:
        name (str): Cat's name.
        age (int): Cat's age.
        features (list): List of features describing the cat.
    """
    try:
        result = cats_collection.insert_one(
            {"name": name, "age": age, "features": features}
        )
        print(f"Cat '{name}' inserted with id: {result.inserted_id}")
    except OperationFailure as e:
        print(f"Error while inserting cat: {e}")


def read_all():
    """Retrieve and print all cat documents from the collection."""
    try:
        for cat in cats_collection.find():
            print(cat)
    except OperationFailure as e:
        print(f"Error while reading data: {e}")


def read_by_name(name):
    """
    Find and print a cat by its name.

    Args:
        name (str): Cat's name to search for.
    """
    try:
        cat = cats_collection.find_one({"name": name})
        if cat:
            print(cat)
        else:
            print(f"No cat found with name '{name}'.")
    except OperationFailure as e:
        print(f"Error while searching for cat: {e}")


def update_age(name, new_age):
    """
    Update a cat's age by its name.

    Args:
        name (str): Cat's name to update.
        new_age (int): New age value.
    """
    try:
        result = cats_collection.update_one(
            {"name": name},
            {"$set": {"age": new_age}}
        )
        if result.modified_count > 0:
            print(f"Age of cat '{name}' updated to {new_age}.")
        else:
            print(f"No cat found with name '{name}' or age already {new_age}.")
    except OperationFailure as e:
        print(f"Error while updating cat age: {e}")


def add_feature(name, feature):
    """
    Add a new feature to a cat's feature list (no duplicates).

    Args:
        name (str): Cat's name to update.
        feature (str): Feature to add.
    """
    try:
        result = cats_collection.update_one(
            {"name": name},
            {"$addToSet": {"features": feature}}
        )
        if result.modified_count > 0:
            print(f"Feature '{feature}' added to cat '{name}'.")
        else:
            print(f"No cat found with name '{name}' or feature already exists.")
    except OperationFailure as e:
        print(f"Error while adding feature: {e}")


def delete_by_name(name):
    """
    Delete a cat document by its name.

    Args:
        name (str): Cat's name to delete.
    """
    try:
        result = cats_collection.delete_one({"name": name})
        if result.deleted_count > 0:
            print(f"Cat '{name}' deleted.")
        else:
            print(f"No cat found with name '{name}'.")
    except OperationFailure as e:
        print(f"Error while deleting cat: {e}")


def delete_all():
    """Delete all cat documents from the collection."""
    try:
        result = cats_collection.delete_many({})
        print(f"Deleted {result.deleted_count} cats.")
    except OperationFailure as e:
        print(f"Error while deleting all cats: {e}")


if __name__ == "__main__":
    # === Create documents ===
    create_doc("barsik", 3, ["walks in slippers", "likes petting", "ginger"])
    create_doc("murka", 5, ["loves sleeping", "eats fish"])

    # === Read a document by name ===
    # read_by_name("barsik")

    # === Update document ===
    # update_age("barsik", 4)
    # add_feature("barsik", "likes sleeping in the sun")

    # === Delete by name ===
    # delete_by_name("barsik")
    # delete_by_name("murka")

    # === Delete all documents ===
    # delete_all()

    # === Read all documents ===
    print("All cats in collection:")
    read_all()
