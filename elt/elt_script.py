import subprocess
import time



def wait_for_postgres(host, max_retries=10, sleep_time=5):
  retries = 0
  while retries < max_retries:
    try:
      result = subprocess.run(["pg_isready", "-h", host], check=True, text=True, capture_output=True)
      if 'accepting connections' in result.stdout:
        print("Postgres is ready!")
        return True
    except subprocess.CalledProcessError as e:
      print("Postgres is not ready yet", e.stdout, e.stderr)
      retries += 1
      time.sleep(sleep_time)
    print(
      f"Postgres is not ready after {retries * sleep_time} seconds. Retrying..."
    )
  return False


if not wait_for_postgres(host="source_postgres"):
  exit(1)

print("Starting the ETL process...")

source_config = {
  "dbname": "source_db",
  "user": "postgres",
  "password": "postgres",
  "host": "source_postgres",
}

destination_config = {
  "dbname": "target_db",
  "user": "postgres",
  "password": "postgres",
  "host": "target_postgres",
}


dump_command = [
  "pg_dump",
  "-h",source_config["host"],
  "-U",source_config["user"],
  "-d",source_config["dbname"],
  "-f","data_dump.sql",
  "-w"
]

subprocess_env = dict(PGPASSWORD=source_config["password"])

subprocess.run(dump_command, env=subprocess_env, check=True)


load_command = [
  "psql",
  "-h",destination_config["host"],
  "-U",destination_config["user"],
  "-d",destination_config["dbname"],
  "-a", "-f", "data_dump.sql",
]


subprocess_env = dict(PGPASSWORD=destination_config["password"])

subprocess.run(load_command, env=subprocess_env, check=True)

print("ETL process completed!")