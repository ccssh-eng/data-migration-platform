from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower

spark = SparkSession.builder.appName("DataMigration").getOrCreate()

df = spark.read.csv("data_raw/customers_legacy.csv", header=True)

# Transform
df = df.dropDuplicates()
df = df.filter(col("name").isNotNull())
df = df.withColumn("email", lower(col("email")))
df = df.filter(col("email").contains("@"))

# Save
df.write.format("jdbc").option("url", "jdbc:sqlserver://<azure>").option(
    "dbtable", "customers"
).option("user", "user").option("password", "password").mode("append").save()
