
import pyspark
from pyspark.sql import SQLContext
from pyspark.sql.functions import hour, when, col, date_format, to_timestamp, ceil, coalesce

sc = pyspark.SparkContext(appName="HW3-Q1")
sqlContext = SQLContext(sc)


def load_data():
    df = sqlContext.read.option("header",True) \
     .csv("path.csv")
    return df

def pyspark_basic_commands(df):
    '''
    Prints basic PySpark DataFrame operations for reference.
    '''
    print("DataFrame Schema:")
    df.printSchema()
    
    print("\nDataFrame Size:")
    print(f"Rows: {df.count()}, Columns: {len(df.columns)}")
    
    print("\nDataFrame Headers:")
    print(df.columns)
    
    print("\nDataFrame Sample:")
    df.show(5)
    
    print("\nBasic Aggregations:")
    df.select(count("*").alias("total_rows"),
              min("total_amount").alias("min_total_amount"),
              max("total_amount").alias("max_total_amount"),
              avg("total_amount").alias("avg_total_amount"),
              sum("total_amount").alias("sum_total_amount")) \
      .show()
    
    print("\nGroup By Example:")
    df.groupBy("PULocationID").agg(count("*").alias("total_trips")).show(5)
    
    print("\nFilter Example:")
    df.filter(col("passenger_count") > 2).show(5)
    
    print("\nSorting Example:")
    df.orderBy(col("total_amount").desc()).show(5)
