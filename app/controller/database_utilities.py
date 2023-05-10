
from flask import request, jsonify, Blueprint
from flask_restful import Resource
from datetime import datetime
from sqlalchemy import create_engine, func
import pandas as pd
from fastavro import writer, parse_schema
from app.model.models import Employee
from flask_sqlalchemy import SQLAlchemy

database_utilities_blueprint = Blueprint('database_utilities_blueprint', __name__)
db = SQLAlchemy()

connnection_string = 'postgresql://postgres:postgres@localhost:6969/postgres'
output_dir = '/Users/Chuz/Documents/Flask/first_attempt/output_files/'
historical_files_dir = '/Users/Chuz/Documents/Flask/first_attempt/historical_files/'
API_BATCH_PROCESSING_LIMIT = 3

@database_utilities_blueprint.route('/database_utilities')
class DataBaseUtilities(Resource):
    @database_utilities_blueprint.route('/employees_by_quarter', methods=['GET'])
    def employees_by_quarter():
        year = 2021
        q1 = func.date_trunc('quarter', datetime(year, 1, 1))
        q2 = func.date_trunc('quarter', datetime(year, 4, 1))
        q3 = func.date_trunc('quarter', datetime(year, 7, 1))
        q4 = func.date_trunc('quarter', datetime(year, 10, 1))

        data = []
        employees = Employee.query.filter(Employee.datetime >= datetime(year, 1, 1)).all()
        for employee in employees:
            department = employee.department.department
            job = employee.job.job
            quarter = ""
            if employee.datetime >= q1 and employee.datetime < q2:
                quarter = "q1"
            elif employee.datetime >= q2 and employee.datetime < q3:
                quarter = "q2"
            elif employee.datetime >= q3 and employee.datetime < q4:
                quarter = "q3"
            else:
                quarter = "q4"

            found = False
            for d in data:
                if d['department'] == department and d['job'] == job:
                    d[quarter] += 1
                    found = True
                    break

            if not found:
                data.append({
                    'department': department,
                    'job': job,
                    'q1': 0,
                    'q2': 0,
                    'q3': 0,
                    'q4': 0
                })
                for d in data:
                    if d['department'] == department and d['job'] == job:
                        d[quarter] += 1
                        break

        def sort_data(x):
            return (x['department'], x['job'])

        data = sorted(data, key=sort_data)

        return jsonify(data)
    
    @database_utilities_blueprint.route('/departments_more_than_mean', methods=['GET'])
    def departments_more_than_mean():
        year = 2021
        employees = Employee.query.filter(Employee.datetime >= datetime(year, 1, 1)).all()

        department_employees = {}
        for employee in employees:
            if employee.department.department in department_employees:
                department_employees[employee.department.department] += 1
            else:
                department_employees[employee.department.department] = 1

        mean_employees = sum(department_employees.values()) / len(department_employees)

        department_stats = []
        for department, num_employees in department_employees.items():
            if num_employees > mean_employees:
                department_stats.append({
                    'id': department.id,
                    'name': department.department,
                    'num_employees': num_employees
                })

        def sort_stats(x):
            return x['num_employees']

        department_stats = sorted(department_stats, key=sort_stats, reverse=True)

        return jsonify(department_stats)


    @database_utilities_blueprint.route('/avro', methods=['POST'])
    def avro():
        # Get data from request
        data = request.json['data']

        for table in data:
            # Connect to the database using SQLAlchemy
            engine = create_engine(connnection_string)

            # Load the data from the database into a Pandas dataframe
            df = pd.read_sql_table(table, engine)

            # Define the Avro schema for the table
            schema = fastavro.schema.parse_schema({
                "type": "record",
                "name": str(table),
                "fields": [
                    {"name": "id", "type": "int"},
                    {"name": "department", "type": "string"},
                ]
            })

            parsed_schema = parse_schema(schema)

            # 2. Convert pd.DataFrame to records - list of dictionaries
            records = df.to_dict('records')

            # 3. Write to Avro file
            with open(output_dir +'prices.avro', 'wb') as out:
                writer(out, parsed_schema, records)

        return {'message': 'Avro file created successfully'}