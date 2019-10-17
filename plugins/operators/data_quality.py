from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self, redshift_conn_id, table, test_query, expected_res,
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.test_query = test_query
        self.expected_res = expected_res

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        res = redshift.get_records(self.test_query)

        check_details = (
            "Test query: {} | Expected result: {} | Returned result: {}")

        if res is None or len(res[0]) < 1:
            self.log.error(f'No records present in {self.table}')
            raise ValueError(f'No records present in {self.table}')
        elif res[0][0] != self.expected_res:
            self.log.error(f'Table {self.table} failed data quality check')
            self.log.error(check_details.format(self.test_query,
                                                self.expected_res, res[0][0]))
            raise Exception(f'Table {self.table} failed data quality check')

        self.log.info(f'Table {self.table} passed data quality check')
        self.log.info(check_details.format(self.test_query,
                                           self.expected_res, res[0][0]))
