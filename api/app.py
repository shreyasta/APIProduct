"""
Building product API
Name: Shreyasta Samal
Date: 12-05-2019
"""


from flask import Flask
from flask_restful import abort, Api, fields, marshal_with, reqparse, Resource
from model import ProductModel
import status

class ProductManager():
    last_id = 0
    def __init__(self):
        self.products ={}

    def insert_product(self, product):
        self.__class__.last_id += 1
        product.id = self.__class__.last_id
        self.products[self.__class__.last_id] =product

    def get_product(self, id):
        return self.products[id]

    def delete_product(self, id):
        del self.products[id]

# data structure of the response that will be rendered on the Flask API

product_fields ={
    'id': fields.Integer,
    'uri': fields.Url('message_endpoint'),
    'name': fields.String,
    'category': fields.String,
    'brand': fields.String,
    'pricepercountry': fields.Float

}

# Creating an instance of product manager
product_manager = ProductManager()

class Product(Resource):
    def abort_if_message_doesnt_exit(self, id):
        if id not in product_manager.products:
            abort(
                status.HTTP_404_NOT_FOUND,
                message = "Message {0} doesn't exist".format(id))

    @marshal_with(product_fields)
    def get(self, id):
        self.abort_if_message_doesnt_exit(id) # returns not found message if field doesn't exist
        return product_manager.get_product(id) # returns message code if field exists

    def delete(self, id):
        self.abort_if_message_doesnt_exist(id)
        product_manager.delete_product(id)
        return '', status.HTTP_204_NO_CONTENT

    @marshal_with(product_fields)
    def patch(self, id):
        self.abort_if_message_doesnt_exit(id)
        product = product_manager.get_product(id)
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('category', type=str)
        parser.add_argument('brand', type=str)
        parser.add_argument('pricepercountry', type=float)
        args = parser.parse_args()

        if 'name' in args:
            product.name = args['name']
        if 'category' in args:
            product.category = args['category']
        if 'brand' in args:
            product.brand = args['brand']
        if 'pricepercountry' in args:
            product.pricepercountry = args['pricepercountry']
        return product

class ProductList(Resource):
    @marshal_with(product_fields)
    def get(self):
        return [v for v in product_manager.products.values()]

    @marshal_with(product_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank!')
        parser.add_argument('category', type=str, required=True, help='Category cannot be blank!')
        parser.add_argument('brand', type=str, required=True, help='Brand cannot be blank!')
        parser.add_argument('pricepercountry', type=float, required=True, help='Price cannot be blank!')
        args = parser.parse_args()
        product = ProductModel(
            name=args['name'],
            category=args['category'],
            brand=args['brand'],
            pricepercountry = args['pricepercountry']
        )
        product_manager.insert_product(product)
        return product, status.HTTP_201_CREATED


app = Flask(__name__)
api = Api(app)
api.add_resource(ProductList, '/api/products/')
api.add_resource(Product, '/api/products/<int:id>', endpoint='message_endpoint')

if __name__ == '__main__':
    app.run(debug=True)



