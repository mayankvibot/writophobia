# blogging portal

### How to set up?
- Install virtualenv - pip install virtualenv
- Create a virtual environment using command - virtualenv venv
- Activate virtual environment 
  - For Mac/Linux - source venv/bin/activate
  - For Windows - .\venv\Scripts\activate.bat
- Run the py file - python manage.py runserver
- Open a browser and go to http://127.0.0.1:8000 to access the portal

### Creating Super User
- python manage.py createsuperuser 
- Run the above commands and fill the details accordingly
- Now open http://127.0.0.1:8000/admin in a browser to access the admin portal

### Creating Blogs
- The schema works simply, just go to Post table and put the title, description, Category, Subcategory, cover_picture.
- Remember, Category and Subcategory is a Foreign Key Field. You can also put default image in Category and SubCategory.
- Put the content of your blog in ContentToPost table.

#### Blogs Types
- Just put the text or the paragraph in the short_description field, default content_type is text.
- If you want to change the order of the paragraph, just change the priority in ascending order.
- You can put direct HTML code in BlogToContext short_description field, just change content_type to text_html, and it will render the HTML.
- You can put images using the images field, put content_type to image, and short_description will act as description of the image.
- You can put also put programming code box by putting code in the content_type field, and put programming language name in the editor_type field, for ex - python, html.

#### Login/Signup Feature
- Quite simple, handled by Django itself with a bit customization.
