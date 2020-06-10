<h1 align="center">
  A Django-based Ecommerce shop
</h1>

<h2> Summary </h2>

A ecommerce website built using the Django framework 

<h2> Technologies </h2>

* Django web framework
* Javascript
* Bootstrap

<h2> Application Features </h2>

- Home page that displays the list of the products for sale
- Product detail page for information about the product
- Sign up page for user registration
- User login page for users to sign into the app
- Ability for logged in users to add and remove items from their cart
- Order summary page to display all items in users car
- Checkout page to place order
- Ability to add valid coupons/promo codes for a discount
- Stripe integration to pay for orders
- Pagination to limit number of products on the home page

<h2> Techinal Details</h2>

<h3> Project Structure </h3>

The **ecomm_project** folder contains the project settings and the **ecomm** folder contains models, forms, templatates, url
routes for the main application.

<h3> Views </h3>

The app mainly uses of Django base views and some generic views . Generic class-based views like ListView, DetailView are used
home page and the product detail page while the rest of the pages use base view.

<h3> Models </h3>

* **Item** holds information about a product such as title, price, slug url etc.
* **Order Item** links an item to a user and keeps track of the status of an order and the quantity
* **Order** has a many to many relationship to **Order Items** and tracks orders using reference codes. It references 
customer billing and shipping address, payment methods and coupons. It also tracks customer refunds


<h3> Authentication </h3>

For class-based views, authenication is done using Django provided **LoginRequiredMixin**.

<h2> Deployment </h2>
<h3> How to deploy in a local environment </h3>

Run the following command should the web app on **127.0.0.1:8000**

`python manage.py runserver`
