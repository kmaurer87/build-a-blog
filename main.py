import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Body(db.Model): #represents submission from user
    title = db.StringProperty(required = True) #if we don't put a title, python will give an error
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True) #automatically will set the created to the current time

class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')

class MainPage(Handler):
    def render_front(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Body "
                           "ORDER BY created DESC LIMIT 5; ")
        self.render("front.html", title=title, body=body, error=error, posts=posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_front(self, title="", body="", error=""):
        self.render("new_posts.html", title=title, body=body, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Body(title = title, body = body) #don't need to pass in created because it will automatically get that property
            a.put() #stores new artwork in database
            new_page = str(a.key().id())
            self.redirect("/blog/" + new_page)
        else:
            error = "We need a title and some text"
            self.render_front(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        if Body.get_by_id(int(id)) == None:
            error = "<p style='font-family: sans-serif; font-size: 18px; color: red;'>" + "ID number does not exist" + "</p>"
            self.response.write(error)
        else:
            user_id = Body.get_by_id(int(id))
            user_title = "<h1 style='font-family: sans-serif; font-size: 27px;'>" + user_id.title + "</h1>"
            user_body = "<p style='font-family: sans-serif; font-size: 18px;'>" + user_id.body + "</p>"
            content = user_title + user_body
            self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
