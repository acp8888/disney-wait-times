import requests
import pandas as pd
import boto3
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import io

# API endpoint
API_BASE_URL = "https://queue-times.com/en-US/parks"

# Disney park IDs (you may need to verify these)
DISNEY_PARKS = {
    "Disneyland Park": 16,
    "Disney California Adventure": 17
}

def fetch_park_data(park_id):
    response = requests.get(f"{API_BASE_URL}/{park_id}/queue_times.json")
    return response.json()

def process_ride_data(park_name, ride_data):
    current_time = datetime.now(timezone.utc).isoformat()
    return {
        "park_name": park_name,
        "ride_name": ride_data["name"],
        "is_open": ride_data["is_open"],
        "wait_time": ride_data["wait_time"],
        "recorded_at": current_time
    }

def fetch_all_park_data():
    all_ride_data = []
    for park_name, park_id in DISNEY_PARKS.items():
        park_data = fetch_park_data(park_id)
        for land in park_data["lands"]:
            for ride in land["rides"]:
                all_ride_data.append(process_ride_data(park_name, ride))
    return all_ride_data


def save_to_s3(data, bucket_name):
    # Convert data to pandas DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to PyArrow Table
    table = pa.Table.from_pandas(df)

    # Create an in-memory file object
    buffer = io.BytesIO()

    # Write the table to Parquet format in the buffer
    pq.write_table(table, buffer)

    # Reset buffer position
    buffer.seek(0)

    # Generate a filename with current timestamp
    filename = f"disney_park_wait_times.parquet"

    # Upload to S3
    s3 = boto3.client('s3')
    s3.upload_fileobj(buffer, bucket_name, filename)

    print(f"Data saved to S3: s3://{bucket_name}/{filename}")

def main():
    all_ride_data = fetch_all_park_data()
    save_to_s3(all_ride_data, "disney-park-wait-times")

if __name__ == "__main__":
    main()