# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example DAG for the use of the SQLExecuteQueryOperator with Oracle.
"""

from __future__ import annotations

import os
from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "example_oracle"

with DAG(
    dag_id=DAG_ID,
    schedule=None,
    start_date=datetime(2025, 1, 1),
    default_args={"conn_id": "oracle_conn_id"},
    tags=["example"],
    catchup=False,
) as dag:
    # [START howto_operator_oracle]

    # Example of creating a task that calls a common CREATE TABLE sql command.
    create_table_oracle_task = SQLExecuteQueryOperator(
        task_id="create_table_oracle",
        sql=r"""
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE employees (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    name VARCHAR2(50),
                    salary NUMBER(10, 2),
                    hire_date DATE DEFAULT SYSDATE
                )';
            END;
        """,
    )

    # [END howto_operator_oracle]

    insert_data_oracle_task = SQLExecuteQueryOperator(
        task_id="insert_data_oracle",
        sql=r"""
            BEGIN
                INSERT INTO employees (name, salary) VALUES ('Alice', 50000);
                INSERT INTO employees (name, salary) VALUES ('Bob', 60000);
            END;
        """,
    )

    select_data_oracle_task = SQLExecuteQueryOperator(
        task_id="select_data_oracle",
        sql=r"""
            SELECT * FROM employees
        """,
    )

    drop_table_oracle_task = SQLExecuteQueryOperator(
        task_id="drop_table_oracle",
        sql="DROP TABLE employees",
    )

    (create_table_oracle_task >> insert_data_oracle_task >> select_data_oracle_task >> drop_table_oracle_task)

    from tests_common.test_utils.watcher import watcher

    # This test needs watcher in order to properly mark success/failure
    # when "tearDown" task with trigger rule is part of the DAG
    list(dag.tasks) >> watcher()

from tests_common.test_utils.system_tests import get_test_run  # noqa: E402

# Needed to run the example DAG with pytest (see: tests/system/README.md#run_via_pytest)
test_run = get_test_run(dag)
