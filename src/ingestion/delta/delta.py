import pandas as pd
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip


DEFAULT_FORMAT = "delta"


def _create_spark_session(
    app_name: str = "ingestion",
    master_url: str = "local[*]",
) -> SparkSession:
    builder = (
        SparkSession.builder.appName(app_name)
        .master(master_url)
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )
    session = configure_spark_with_delta_pip(builder).getOrCreate()
    session.sparkContext.setLogLevel("ERROR")
    return session


class Delta:
    def __init__(self) -> None:
        self._spark_session: SparkSession | None = None

    @property
    def spark_session(self):
        if not self._spark_session:
            self._spark_session = _create_spark_session
        return self._spark_session

    def write(
        self,
        data: pd.DataFrame,
        path: str,
        *,
        format: str = DEFAULT_FORMAT,
        mode: str = "append",
        show: bool = False,
    ):
        dataframe = self.spark_session.createDataFrame(data)

        if show:
            dataframe.show(truncate=False)

        dataframe.write.format(format).mode(mode).save(path)

    def read(
        self,
        path: str,
        *,
        format: str = DEFAULT_FORMAT,
    ) -> pd.DataFrame:
        data = self.spark_session.read.format(format).load(path)
        return pd.DataFrame(data.toPandas())

    def show(
        self,
        path: str,
        query: str = "*",
        *,
        format: str = DEFAULT_FORMAT,
    ):
        self.spark_session.read.format(format).load(path).select(query).show()
