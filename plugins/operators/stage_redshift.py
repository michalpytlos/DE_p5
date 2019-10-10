from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    copy_query = """
    COPY {}
        FROM '{}'
        CREDENTIALS 'aws_iam_role={}'
        REGION '{}'
        FORMAT AS JSON '{}'
        MAXERROR AS 1000
    """

    @apply_defaults
    def __init__(self, redshift_conn_id, table, s3_bucket, s3_prefix,
                 arn, region='us-west-2', json_path=None, *args, **kwargs):
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.arn = arn
        self.region = region
        self.json_path = json_path

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        s3_path = f's3://{self.s3_bucket}/{self.s3_prefix}'

        if self.json_path:
            json_option = f's3://{self.s3_bucket}/{self.json_path}'
        else:
            json_option = 'auto'

        query = StageToRedshiftOperator.copy_query.format(
            self.table,
            s3_path,
            self.arn,
            self.region,
            json_option
        )

        self.log.info(f'Copying data from S3 to Redshift ({self.table})')
        redshift.run(query)
        self.log.info(f'Copy completed ({self.table})')
