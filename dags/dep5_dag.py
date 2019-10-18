from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# Default args for each task of the DAG
default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# DAG
dag = DAG('dep5_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 0 1 1 *'
          )

# Tasks
start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id='redshift',
    table='staging_events',
    s3_bucket=Variable.get('s3_bucket'),
    s3_prefix=Variable.get('s3_log_prefix'),
    arn=Variable.get('iam_role_arn'),
    json_path=Variable.get('s3_log_jsonpath')
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id='redshift',
    table='staging_songs',
    s3_bucket=Variable.get('s3_bucket'),
    s3_prefix=Variable.get('s3_song_prefix'),
    arn=Variable.get('iam_role_arn'),
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='songplays',
    insert_query=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='users',
    insert_query=SqlQueries.user_table_insert,
    delete_load=False
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='songs',
    insert_query=SqlQueries.song_table_insert,
    delete_load=False
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='artists',
    insert_query=SqlQueries.artist_table_insert,
    delete_load=False
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='time',
    insert_query=SqlQueries.time_table_insert,
    delete_load=False
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id='redshift',
    table='songplays',
    test_query='SELECT COUNT(*) FROM songplays WHERE song_id IS NULL',
    expected_res=0
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

# Set task dependencies
start_operator >> (stage_events_to_redshift, stage_songs_to_redshift)
(stage_events_to_redshift, stage_songs_to_redshift) >> load_songplays_table
load_songplays_table >> (load_artist_dimension_table,
                         load_song_dimension_table,
                         load_user_dimension_table,
                         load_time_dimension_table) >> run_quality_checks
run_quality_checks >> end_operator
