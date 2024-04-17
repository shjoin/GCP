from pyspark import SparkConf
from pyspark.sql import *

##SparkSession is a driver spark=SparkSession.builder.appName("Hello Spark").master("local[3]").getOrCreate()
##SparkSession is a driver spark=SparkSession.builder.config(conf=SparkConf()).getOrCreate()


if __name__ == "__main__":
  
    
       confobj= SparkConf()
       confobj.set("spark.app.name","HelloSpark")
       confobj.set("spark.master","local[3]")
      #if we use sparkconf as above , no need define in sparksession as below ,we just need to pass this conf object in sparksession   
           
   
    spark = SparkSession.builder \
        .config(conf=confobj)       
         #.appName("HelloSpark") \
         #.master("local[2]") \
        .getOrCreate()
        
precedence for spark config details read by Spark-submit 
4)environment variable 
3)spark-defaults.conf        
2)comnand line option -best 
1)application code -best 

a)Spark-submit run  (
b)local run 

spark-submit-->
spark properties into two categories   (best practice should be in command line  )
1) Deployement /resources 
  a ) driver.memory
  b)  executor.instances

2) run time behavior (best practice should be in application code )
  a) task.maxFalures
  b) Shuffle.partitions
  
  
  couple of configurations should not be hardcoded because we work in local and test our code in locally so we need toconfigure master as Local  and deploy in cluster and 
  we dont know about the resource manager would be yarn or ...?
  
        SparkSession.builder \
        .config(conf=confobj)       
         #.appName("HelloSpark") \
         #.master("local[2]") \
         
so we can create spark.conf file with storing all details with using sections like below 


spark.conf -->

[SPARK_APP_CONFIGS]
spark.app.name = HelloSpark
spark.master = local[3]
spark.sql.shuffle.partitions = 2

folder:lib
   utils.py-->

import configparser
from pyspark import SparkConf

def get_spark_app_config():
    spark_conf = SparkConf()
    config = configparser.ConfigParser()
    config.read("spark.conf")

    for (key, val) in config.items("SPARK_APP_CONFIGS"):
        spark_conf.set(key, val)
    return spark_conf
    
    

def read_csv_df(spark, data_file):
    return spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(data_file)


def count_by_country(survey_df):
    return survey_df.filter("Age < 40") \
        .select("Age", "Gender", "Country", "state") \
        .groupBy("Country") \
        .count()


  
    

HelloSpark.py-->

from pyspark.sql import * 
from lib.utils import *


if "__name__ == __main__":
  confobj =get_spark_app_config()
  spark = SparkSession.builder \
           .config(conf=confobj) \
           .getOrCreate()
           
           
    conf_out = spark.sparkContext.getConf()
    print(conf_out.toDebugString())
    
   we are going to use this steps more than two so we can use this through methode above read_csv_df
   # df = spark.read \
    #.option("header","true") \
    #.option("header","true") \
    #.option("inferSchema","true") \    
    #.csv(file_name)
    file_df= read_csv_df(spark,file_name)
    file_df.show(10)
    
   # now time to transform this data 
   filtered_df = file_df.where("Age < 40") \
                        .select("Age","Gender","Country","state")   
   grouped_df= filtered_df.groupBy("Country")
   count_df = grouped_df.count()
   count_df.show(10)
   
   two type TRansfomation -->
    a) Narrow dependency (where clause )
    b) Wide dependency (Group by,order by ,join ,distinct )
    
    Actions are 
    1)read 2) Write 3 collect 4.show
    
    
    3 )collect --> Collect the result from executors to the driver 
    1) Read --> read a data file to infer the column names and schema .
    
    So Spark actions will terminate the transformation DAG and trigger the execution.that is why we say that the transformations are LAZY BUT Actions are evaluated immediately  .
    
    Tranformations ***-- anything which takes one df to converts into another df is a transformation.
    Action ***- But Operations that require you to read ,write ,collect to show the data is an Action.
    
       *** Read***
       file_df= read_csv_df(spark,file_name) -->Read and infering the schema the result is a data Frame 
        Partitioned_file_df = file_df.repartition(2) --> its a  transformation and now this DF has two partitions 
       
       **** applying the Chain on transformation and the result is a data Frame ****
               filtered_df = Partitioned_file_df.where("Age < 40") \
                                .select("Age","Gender","Country","state")   
               grouped_df= filtered_df.groupBy("Country")
               count_df = grouped_df.count()
    
 
        *** Action ***
          count_df.show(10)
    
    
Spark Compiles and it generate low level spark code and also creates an execution plan            
           
***********************************************************************************************************

def count_by_country(survey_df):
    return survey_df.filter("Age < 40") \
        .select("Age", "Gender", "Country", "state") \
        .groupBy("Country") \
        .count()
        
        

*** Read***
       file_df= read_csv_df(spark,file_name) -->Read and infering the schema the result is a data Frame 
        Partitioned_file_df = file_df.repartition(2) --> its a  transformation and we forcefully to make sure
        that we get two partitions here and now this DF has two partitions.However ,we dont know how many partiotions will 
        result the shuffle/short .
        But we want to control this behaviour with using spark.sql.shuffle.partitions = 2 
        
Shuffle short caused by the group by will result inn only two partitions .So we made sure that the whole transformation flow
is accomplished with two partiotions.        
        
        
  [SPARK_APP_CONFIGS]
spark.app.name = HelloSpark
spark.master = local[3]
spark.sql.shuffle.partitions = 2 --> added shuffle.partition =2 

as we know that we are applying a wide dependency transformation groupby 
so , the group by is going to result in an insternal repartitioning caused by the shuffle short 


we can see sparkUI localhost:4040
RDD API 
 -->Catalyst Optimizer (know as the SPARK SQL ENGINE /it is powerfull compiler ,generates effeciate JavaBytecode )
    -->Spark SQL       best #1
    -->DataFrame API   best #2
    -->Dataset API     Best #3 jvm based language like scala or JAva
     
     ***IMP - all these API are internally powered by something know as the SPARK SQL ENGINE.
      
   
   **** Imp theory***** 
        Python wrapper calls the java wrapper with using py4j connector .pyrj allws a python application to call a java application.it will
        always start a JVM application ans call spark API in the JVM.
        
        Actual spark application is always a scala application running in the JVM.
        
         SPARK SQL ENGINE (Catalyst Optimizer) broken down in four phases 
               1. Analysis
               2.Logical optimization
               3.Physical Planning 
               4.Code generation
        
        Analysis - SSQL engin read our code and generates an abstract syntax tree for our SQL 
        col name ,table ,sql function , view are resolved on this Phase .we can get run time error shows as an analysis aerror 
        at this stage when your names dont resolve .
        Logical optimization- construct multiple execution plan .cost base optiomization.
        
        Physical Planning- the sql engin picks the mose effective logical plan and generates the pysical plan is nothing but a set of RDD operations which dettermine how the plan is going to execute on spark cluster .
        
        Code generation- generates java bytecode to run on each machine .
        
        Resourese:  Kubernates / Yarn/mesos
        
        
        
        
        **********************************SPARK SQL********************
        
        ssql_df= createOrReplaceTempView("tableA_vw")
        countDF = spark.sql("select country,count(1) as count from tableA_vw where age>5 group by Country")
        countDF.show()
        
        
        
        *******************Data Frame API*****************
               
        https://spark.apache.org/docs/3.2.0/api/python/reference/pyspark.sql.html#data-types
        
        schema for Dataframe 
            Explicit 
            implicit (parquet file have schema implicitly )
                         
            
        
          spark.read.option("inferSchema","true")            
                     **Json does not come with header          
      
        
        Spark Data Types-->
                ArrayType(elementType[, containsNull])    Array data type.
                BinaryType                                Binary (byte array) data type.
                BooleanType                         Boolean data type.
                ByteType                            Byte data type, i.e.
                DataType                            Base class for data types.
                DateType                            Date (datetime.date) data type.
                DecimalType([precision, scale])         Decimal (decimal.Decimal) data type.
                DoubleType                              Double data type, representing double precision floats.
                FloatType                           Float data type, representing single precision floats.
                IntegerType                         Int data type, i.e.
                LongType                                Long data type, i.e.
                MapType(keyType, valueType[, valueContainsNull])                Map data type.
                NullType                                     Null type. 
                ShortType                                       Short data type, i.e.
                StringType                                      String data type.
                StructField(name, dataType[, nullable, metadata])           A field in StructType.
                StructType([fields])                                       Struct type, consisting of a list of StructField.
                TimestampType                                       Timestamp (datetime.datetime) data type.

CREATE SChema-->
          flightSchemaStruct = StructType([
                StructField("FL_DATE", DateType()),
                StructField("OP_CARRIER", StringType()),
                StructField("OP_CARRIER_FL_NUM", IntegerType()),
                StructField("ORIGIN", StringType()),
                StructField("ORIGIN_CITY_NAME", StringType()),
                StructField("DEST", StringType()),
                StructField("DEST_CITY_NAME", StringType()),
                StructField("CRS_DEP_TIME", IntegerType()),
                StructField("DEP_TIME", IntegerType()),
                StructField("WHEELS_ON", IntegerType()),
                StructField("TAXI_IN", IntegerType()),
                StructField("CRS_ARR_TIME", IntegerType()),
                StructField("ARR_TIME", IntegerType()),
                StructField("CANCELLED", IntegerType()),
                StructField("DISTANCE", IntegerType())
    ])
    
    We can remove infer schema and use this schema 
    
    #spark.read.option("inferSchema","true")            
                     **Json does not come with header

df = spark.read \
    .option("header","true") \
    .schema(flightSchemaStruct)
    #.option("inferSchema","true") \    
    .csv(file_name)
    
    OR 
    
    df = spark.read \
    .format('csv')
    .option("header","true") \
    .schema(flightSchemaStruct)
    #.option("inferSchema","true") \    
    .option("mode","FAILFAST")
    .option("dateFormat","M/d/y") \  --> Need to fix for datetime 
    .load(file_name) \
    
    Lets Try to learn DDL string 
   
     flightSchemaDDL = """FL_DATE DATE, OP_CARRIER STRING, OP_CARRIER_FL_NUM INT, ORIGIN STRING, 
          ORIGIN_CITY_NAME STRING, DEST STRING, DEST_CITY_NAME STRING, CRS_DEP_TIME INT, DEP_TIME INT, 
          WHEELS_ON INT, TAXI_IN INT, CRS_ARR_TIME INT, ARR_TIME INT, CANCELLED INT, DISTANCE INT"""
    
     df = spark.read \
    .format('csv')
    .option("header","true") \
    .schema(flightSchemaDDL)
    #.option("inferSchema","true") \    
    .option("mode","FAILFAST")
    .option("dateFormat","M/d/y") \  --> Need to fix for datetime 
    .load(file_name) \
        

https://spark.apache.org/docs/3.2.0/api/python/_modules/pyspark/sql/readwriter.html#DataFrameReader.csv
    
    three Read modes -->
    .option("mode","FAILFAST")
    1)Permissive
    2)Dropmalformed
    3)failfast
    
    
    
    
    ***************************** dataframeWriter***************************
    DataFrameWriter.format()
        .mode("overwrite") \
        .option("path", "dataSink/json/") \
        .partitionBy("OP_CARRIER", "ORIGIN") \
        .option("maxRecordsPerFile", 10000) \
        .save()

          Save mode -->
                1)append 
                2)overwrite
                3)errorifExists
                4)ignore
                
                    
 flightTimeParquetDF = spark.read \
        .format("parquet") \
        .load("dataSource/flight*.parquet")

    logger.info("Num Partitions before: " + str(flightTimeParquetDF.rdd.getNumPartitions()))
    flightTimeParquetDF.groupBy(spark_partition_id()).count().show()
    
    --> str(flightTimeParquetDF.rdd.getNumPartitions())) return : 2 and two files (one has nothing )
    --> partition_id 0 and count 4704771 

    partitionedDF = flightTimeParquetDF.repartition(5)
    logger.info("Num Partitions after: " + str(partitionedDF.rdd.getNumPartitions()))
    partitionedDF.groupBy(spark_partition_id()).count().show()
    
     --> str(flightTimeParquetDF.rdd.getNumPartitions())) return : 5 and also I got 5 files 
    --> partition_id 0 and count 940951
                     1 and count 940961
                     3 and count 940951
                     4 and count 940951
                     5 and count 940961
    

    partitionedDF.write \
        .format("avro") \
        .mode("overwrite") \
        .option("path", "dataSink/avro/") \
        .save()

    flightTimeParquetDF.write \
        .format("json") \
        .mode("overwrite") \
        .option("path", "dataSink/json/") \
        .partitionBy("OP_CARRIER", "ORIGIN") \
        .option("maxRecordsPerFile", 10000) \
        .save()
    
    parttitioned on basis on columns "OP_CARRIER", "ORIGIN"
    
    ********************Spark database and tables 
    
    databse:
       1 Tables ---> Tables data (spark warehouse)     
       2 Views ---> (table metadata ) catalog metastore
       
       Spark tables :
           1. managed tables  ---sales table---> spark warehouse , --create table--->Table metadata 
           2. unmanaged tables (external tables)  : --created table for existing data ----> table metadata 
               Createt bale table_name (col1 data type , ... 
               )
               Using Parquet 
               location "data _file_loaction"
               
         
        Lets say you have data in file in some where and you want to run on spark sql select * from ...
        we have to create unmanaged table and map the same ddata to spark table and now spark will create metadata and store it .
        if we drop managed table ,spark will delete the metadata and data as well .
        if we drop unmamaged table ,spark removes the metadata and do not touch the data file .
         becase unmanaged tables are designed for temporarily mapping ur existsing data and using it in spark sql .
         
         best is managed table 
         
         *****need to enable .enableHiveSupport()
         
         
         spark = SparkSession \
        .builder \
        .master("local[3]") \
        .appName("SparkSQLTableDemo") \
        .enableHiveSupport() \
        .getOrCreate()
        
        
        flightTimeParquetDF = spark.read \
        .format("parquet") \
        .load("dataSource/")

    spark.sql("CREATE DATABASE IF NOT EXISTS AIRLINE_DB") --> need to create a DB
    spark.catalog.setCurrentDatabase("AIRLINE_DB") --> set the our newly data base as current 

    flightTimeParquetDF.write \
        .mode("overwrite") \
        .partitionBy("ORIGIN","OP_CARRIER")
        .saveAsTable("flight_data_tbl")

  we are saving Dataframe flight_data_tbl in managed table in spark default database (name is Default data base) , why we are not saving data as parquet / avro/json/csv in managed table ,because these files are not accessible throughJDBC/ODBC interface.
  
  catalog gives us access to the whole bunch of metadata information.
     spark.catalog.listTables("AIRLINE_DB")
  
  spark-warehouse folder will creates and under this db name folder --> tablename --> files
  
  here we used .partitionBy("ORIGIN","OP_CARRIER") and we have 200+ different origins so we got 200+ partitions .
 what about 100k unique valies on my partition column 
 --> do I need to create 100k partitions ?
    so best way bucketBy(5,"ORIGIN","OP_CARRIER")
 
 
 flightTimeParquetDF.write \
        .mode("overwrite") \
        .bucketBy(5,"ORIGIN","OP_CARRIER") --> does not require lenghy directory structure 
        .sortBy("OP_CARRIER","ORIGIN") --> sorting 
        .saveAsTable("flight_data_tbl")
        
        only 5 files will generate . spark-warehouse -->AIRLINE_DB db name folder --> tablename flight_data_tbl --> 5 files.
        
        
       Spark Data Frame is a Dataset  of row
        
        PySpark parallelize() :-->
        is a function in SparkContext and is used to create an RDD from a list collection. In this article, I will explain the usage of parallelize to create RDD and how to create an empty RDD with PySpark example
        
 def to_date_df(df, fmt, fld):
    return df.withColumn(fld, to_date(fld, fmt))    

       my_schema = StructType([
        StructField("ID", StringType()),
        StructField("EventDate", StringType())])

    my_rows = [Row("123", "04/05/2020"), Row("124", "4/5/2020"), Row("125", "04/5/2020"), Row("126", "4/05/2020")]
    my_rdd = spark.sparkContext.parallelize(my_rows, 2)
    my_df = spark.createDataFrame(my_rdd, my_schema)   
   
   we can not assert the data frame . if you want to validate the data , then you must bring it to the driver .The collect() methode is return list of rows to our driver .
   
    rows = to_date_df(self.my_df, "M/d/y", "EventDate").collect()
    for row in rows:
       assertIsInstance(row["EventDate"],date)
       
       
       assertIsInstance() in Python is a unittest library function that is used in unit testing to check whether an object is an instance of a given class or not. This function will take three parameters as input and return a boolean value depending upon the assert condition. If the object is an instance ofthe given class it will return true else it returns false.
       
    
***********Process Unstructure data     
    file_df = spark.read.text("data/apache_logs.txt")
    file_df.printSchema()

    log_reg = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\S+) "(\S+)" "([^"]*)'

    logs_df = file_df.select(regexp_extract('value', log_reg, 1).alias('ip'),
                             regexp_extract('value', log_reg, 4).alias('date'),
                             regexp_extract('value', log_reg, 6).alias('request'),
                             regexp_extract('value', log_reg, 10).alias('referrer'))

    logs_df \
        .where("trim(referrer) != '-' ") \
        .withColumn("referrer", substring_index("referrer", "/", 3)) \ ----> Column level transformation 
        .groupBy("referrer") \
        .count() \
        .show(100, truncate=False)

************Column level transformation
        
        If schema inference is needed, samplingRatio is used to determined the ratio of rows used for schema inference. The first row will be used if samplingRatio is None.
        
        spark.read \
        .format ("csv") \
        .option("header","true") \
        .option("inferSchema","true") \
        .option("samplingRatio","0.0001")  \
        .load ("/databricks-datasets/airlines/part-00000")
        
        Spark data frame coulmns are objects of type column.
        there are two ways to refer to columns in a dataframe transformation .
         1 Column String
         2 Column Object
         
         
        Column String: -->airlineDF.select ("Orgin", "Dest","Destance","year").show(10)
        Column Object:--> from pyspark.sql.function import *
                          airlineDF.select (column("Orgin"), col("Dest"),airlineDF.Destance,"year").show(10)
                          ###three ways to get column object above
                          
       ******Spark DataFrame offers multiple ways to create column expression  :
                   1)String Expressions or SQL Expressions        
                   2)Column Object Expressions
                   
       
       if we want to create an expression with using multiple columns we can not use Select function because Select uses only for string and object SO we should use expr() function here 
          airlineDF.select (column("Orgin"), col("Dest"),airlineDF.Destance,"year","month","DayofMonth").show(10)
           
          airlineDF.select (column("Orgin"), col("Dest"),airlineDF.Destance,"year","month","DayofMonth").show(10)
           
         DoesNOT  work with select function to_date(concat(year,month,dayofMonth),'yyyyMMdd' ) as FlightDate
      
       1. String Expressions or SQL Expressions  
                Solution : this expr funxction to convert an expression to a column object .expr is going to parse the expression and  return a column object.
               
               airlineDF.select("Orgin", "Dest","Destance",expr("to_date(concat(year,month,dayofMonth),'yyyyMMdd' ) as FlightDate"))
               
       2.Column Object Expressions-->
              airlineDF.select("Orgin", "Dest","Destance",to_date(concat("year","month","dayofMonth"),'yyyyMMdd' ) alias ("FlightDate")).show(10)
        
        
        DataFrame
        column
        Built-in -Functions 
        
    UDF-->    Lets say we have gender column values Female ,M ,Male ,F in our dataset file  and want to standardize like 
               MALE,FEMALE,UNKNOWN
         
       Custom Function  -->
                     def parse_gender(gender):
                            female_pattern = r"^f$|f.m|w.m"
                            male_pattern = r"^m$|ma|m.l"
                            if re.search(female_pattern, gender.lower()):
                                return "Female"
                            elif re.search(male_pattern, gender.lower()):
                                return "Male"
                            else:
                                return "Unknown"       
               
    survey_df.withColumn() --> transformation allows you to transform a single column without impacting other columns in the DF.
                                  here parse_gender_udf supply the genger column value .
                                 However we cannot simply use a function in a column object expresion.
                               I need to register my custom function to the driver and make it a UDF.  
              parse_gender_udf = udf(parse_gender, returnType=StringType()) #register my custom function to the driver                     
              survey_df2 = survey_df.withColumn("Gender", parse_gender_udf("Gender"))
    
    1_)Create custom Function
    2)Register it as UDF 
    3)Get the reference. 
    (Now function is registered in spark Session and our driver will Serialize and send this function to the Executors .Executor can run this function.
    now we can use our function in our expression .
    
    WE CAN use it in a String or SQL expression -->
                  : we need to register it as a SQL Function , and it should go to the catalog wuth using spark.udf.register.    
     
     spark.udf.register("parse_gender_udf_cat", parse_gender, StringType())
     survey_cat_df3 = survey_df.withColumn("Gender", expr("parse_gender_udf_cat(Gender)")) ---withcolumn does not take SQL 
     Expression .now Spark engin will parse this string at runtime ans resolve the UDF and column name from Catalog.
     
     
     
    
    ################################UDEMY CODE BELOW 
         parse_gender_udf = udf(parse_gender, returnType=StringType())
    logger.info("Catalog Entry:")
    [logger.info(r) for r in spark.catalog.listFunctions() if "parse_gender" in r.name]

    survey_df2 = survey_df.withColumn("Gender", parse_gender_udf("Gender"))
    survey_df2.show(10)

    spark.udf.register("parse_gender_udf", parse_gender, StringType())
    logger.info("Catalog Entry:")
    [logger.info(r) for r in spark.catalog.listFunctions() if "parse_gender" in r.name]

    survey_df3 = survey_df.withColumn("Gender", expr("parse_gender_udf(Gender)"))
    survey_df3.show(10)
   #################################################################### 
    
    
    ******************miscellaneous 
    
    from pyspark.sql.functions import col, monotonically_increasing_id, when, expr
    
     data_list = [("Ravi", "28", "1", "2002"),
                 ("Abdul", "23", "5", "81"),  # 1981
                 ("John", "12", "12", "6"),  # 2006
                 ("Rosy", "7", "8", "63"),  # 1963
                 ("Abdul", "23", "5", "81")]  # 1981

    raw_df = spark.createDataFrame(data_list).toDF("name", "day", "month", "year").repartition(3)
    raw_df.printSchema()

    final_df = raw_df.withColumn("id", monotonically_increasing_id()) \
        .withColumn("day", col("day").cast(IntegerType())) \
        .withColumn("month", col("month").cast(IntegerType())) \
        .withColumn("year", col("year").cast(IntegerType())) \
        .withColumn("year", when(col("year") < 20, col("year") + 2000)  
                    .when(col("year") < 100, col("year") + 1900)
                    .otherwise(col("year"))) \
        .withColumn("dob", expr("to_date(concat(day,'/',month,'/',year), 'd/M/y')")) \
        .drop("day", "month", "year") \
        .dropDuplicates(["name", "dob"]) \
        # .sort(expr("dob desc")) This doesn't seem to be working
        .sort(col("dob").desc())

    final_df.show()
    
    
    
    
        --inline cast
        .withColumn("year", ,expr("""case when year < 21 then cast(year as int) + 2000 
                                           when year < 100 then cast (year as int) + 1900
                                           else year
                                           end"""))
                                           
        ---change the schema (changing our schema is a choice thet I need to make 
        .withColumn("year", ,expr("""case when year < 21 then year + 2000 
                                           when year < 100 then year  + 1900
                                           else year
                                           end""")).cast(IntergerType()))
                                           
        we can cast all three column -->
               DF_1= raw_df.withColumn("day", col("day").cast(IntegerType())) \
                      .withColumn("month", col("month").cast(IntegerType())) \
                      .withColumn("year", col("year").cast(IntegerType())) 
               
               DF_2= DF_1.withColumn("year",expr("""case when year < 21 then year + 2000 
                                                         when year < 100 then year + 1900
                                                         else year
                                                         end"""))                       
    
     --BEST WAY-->
      DF_1= raw_df.withColumn("day", col("day").cast(IntegerType())) \
                      .withColumn("month", col("month").cast(IntegerType())) \
                      .withColumn("year", col("year").cast(IntegerType())) 
                      
      DF_3=  DF_1.withColumn("year", when(col("year") < 20, col("year") + 2000)  
                           .when(col("year") < 100, col("year") + 1900)
                           .otherwise(col("year"))) 
                           
          DF_3.show()                 
                           
     DF_4= DF_3.withColumn("dob",expr("to_date(concat(day,'/',month,'/',year),'d/m/y')"))
     DF_4.show()
     
     DF_5= DF_3.withColumn("dob",to_date(expr("concat(day,'/',month,'/',year),'d/m/y')))
               .drop("day","month","year") 
               .dropDuplicates(["name","dob"]) -- on basis 
               
     
     
     
        
***********************************************MY ADVANCE TOPICS***************        
        https://spark.apache.org/docs/3.2.0/api/python/reference/api/pyspark.sql.DataFrame.html?highlight=pyspark%20sql%20dataframe#pyspark.sql.DataFrame
        
          https://spark.apache.org/docs/3.2.0/api/python/reference/pyspark.sql.html
                                
                https://spark.apache.org/docs/3.2.0/api/python/reference/pyspark.sql.html#functions
                
                
                https://spark.apache.org/docs/3.2.0/api/python/reference/pyspark.sql.html#window
                
        
        pyspark.sql.DataFrame.filter
        DataFrame.filter(condition)
        
        Filters rows using the given condition.
           where() is an alias for filter().         

            Parameters:condition: Column or str
                   a Column of types.BooleanType or a string of SQL expression.

                Examples

                >>>
                df.filter(df.age > 3).collect() --> Column Expression 
                [Row(age=5, name='Bob')]
                df.where(df.age == 2).collect()
                [Row(age=2, name='Alice')]
                >>>
                df.filter("age > 3").collect() --->string of SQL expression
                [Row(age=5, name='Bob')]
                df.where("age = 2").collect()
                [Row(age=2, name='Alice')]
                
                so we can do the same thing creating an expresion using the column object or using the string expression like this 
                
              
                
                 Examples
        --------
        >>> from pyspark.sql import Window
        >>> from pyspark.sql import functions as func
        >>> from pyspark.sql import SQLContext
        >>> sc = SparkContext.getOrCreate()
        >>> sqlContext = SQLContext(sc)
        >>> tup = [(1, "a"), (1, "a"), (2, "a"), (1, "b"), (2, "b"), (3, "b")]
        >>> df = sqlContext.createDataFrame(tup, ["id", "category"])
        >>> window = Window.partitionBy("category").orderBy("id").rowsBetween(Window.currentRow, 1)
        >>> df.withColumn("sum", func.sum("id").over(window)).sort("id", "category", "sum").show()
        +---+--------+---+
        | id|category|sum|
        +---+--------+---+
        |  1|       a|  2|
        |  1|       a|  3|
        |  1|       b|  3|
        |  2|       a|  2|
        |  2|       b|  5|
        |  3|       b|  3|
        
        
        Window
Window.currentRow  

Window.orderBy(*cols) Creates a WindowSpec with the ordering defined. 

Window.partitionBy(*cols) Creates a WindowSpec with the partitioning defined.

Window.rangeBetween(start, end) Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).

Window.rowsBetween(start, end) Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).

Window.unboundedFollowing Window.unboundedPreceding

WindowSpec.orderBy(*cols)  Defines the ordering columns in a WindowSpec.

WindowSpec.partitionBy(*cols)  Defines the partitioning columns in a WindowSpec.

WindowSpec.rangeBetween(start, end) Defines the frame boundaries, from start (inclusive) to end (inclusive).

WindowSpec.rowsBetween(start, end) Defines the frame boundaries, from start (inclusive) to end (inclusive).

Grouping

GroupedData.agg(*exprs)  Compute aggregates and returns the result as a DataFrame.

GroupedData.apply(udf) It is an alias of pyspark.sql.GroupedData.applyInPandas(); however, it takes a pyspark.sql.functions.pandas_udf() whereas pyspark.sql.GroupedData.applyInPandas() takes a Python native function.

GroupedData.applyInPandas(func, schema) Maps each group of the current DataFrame using a pandas udf and returns the result as a DataFrame.

GroupedData.avg(*cols) Computes average values for each numeric columns for each group.

GroupedData.cogroup(other) Cogroups this group with another group so that we can run cogrouped operations.

GroupedData.count() Counts the number of records for each group.

GroupedData.max(*cols) Computes the max value for each numeric columns for each group.

GroupedData.mean(*cols) Computes average values for each numeric columns for each group.

GroupedData.min(*cols) Computes the min value for each numeric column for each group.

GroupedData.pivot(pivot_col[, values]) Pivots a column of the current DataFrame and perform the specified aggregation.

GroupedData.sum(*cols) Computes the sum for each numeric columns for each group.

PandasCogroupedOps.applyInPandas(func, schema) Applies a function to each cogroup using pandas and returns the result as a DataFrame.

**********************************************************************************************************

