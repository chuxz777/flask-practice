from flask_restful import Api
from flask import Blueprint

from .employees import EmployeeResource
from .jobs import JobResource
from .departments import DepartmentResource
from .database_utilities import DataBaseUtilities

api = Api()
api.add_resource(EmployeeResource, '/employees', '/employees/<int:employee_id>')
api.add_resource(JobResource, '/jobs', '/jobs/<int:job_id>')
api.add_resource(DepartmentResource, '/departments', '/departments/<int:department_id>')
api.add_resource(DataBaseUtilities, '/database_utilities')

employees_blueprint = Blueprint('employees', __name__)
api.init_app(employees_blueprint)

jobs_blueprint = Blueprint('jobs', __name__)
api.init_app(jobs_blueprint)

departments_blueprint = Blueprint('departments', __name__)
api.init_app(departments_blueprint)

database_utilities_blueprint = Blueprint('database_utilities', __name__)
api.init_app(database_utilities_blueprint)