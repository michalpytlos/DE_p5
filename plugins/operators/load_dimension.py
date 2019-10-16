from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self, redshift_conn_id, table, insert_query, delete_load,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.insert_query = insert_query
        self.delete_load = delete_load

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.delete_load:
            self.log.info(f'Deleting data from {self.table}')
            redshift.run(f'DELETE FROM {self.table}')
            self.log.info(f'Delete completed ({self.table})')

        self.log.info(f'Loading data to {self.table}')
        redshift.run(self.insert_query.format(self.table))
        self.log.info(f'Load completed ({self.table})')
