import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def create_app(test_config= None,):
  # create and configure the app
  app = Flask(__name__,instance_relative_config=True)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response




  def paginate_Questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''


  @app.route('/categories',methods=['GET'])
  def retrieve_categories():
    '''
    an endpoint to handle GET requests 
    for allavailablecategories.
    '''
    selection = Category.query.order_by(Category.id).all()

    categories = {}
    for category in selection:
      categories[category.id] = category.type
    


    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories
    })



  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  #tested
  @app.route('/questions')
  def retrieve_questions():
    '''
      an endpoint to handle GET requests for questions
      returns total questions, current category, categories
    '''

    question_selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_Questions(request, question_selection)

    if len(current_questions) == 0:
      abort(404)

    # categories_selection = Category.query.order_by(Category.id).all()
    # categories = [category.format() for category in categories_selection]
    categories = {}
    for category in Category.query.all():
      categories[category.id] = category.type

  


    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': categories,
      # 'current_category': 'none'
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  #tested
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    '''
    an endpoint to DELETE question using a question ID
    '''
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_Questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)





  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  #tested
  @app.route('/questions', methods=['POST'])
  def create_question():

    '''
    a POST endpoint the creates a new question
    '''
    try:

      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      difficulty = body.get('difficulty', None)
      
      question = Question(question=new_question,
                          answer=new_answer,
                          difficulty=difficulty,
                          category=new_category)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_Questions(request, selection)

      return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  ##tested
  @app.route('/search', methods=['POST'])
  def search():
    '''
    a POST endpoint that takes a search term and return list of questions that contains it
    '''

    # categories = Category.query.all()
    body = request.get_json()


    search = body.get('searchTerm',None)

    selection = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
    questions = paginate_Questions(request, selection)

    if (len(selection) == 0):
          abort(404)




    return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': len(questions)
    })

  




  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #tested
  @app.route('/categories/<int:c_id>/questions')
  def questions_by_catagory(c_id):

    '''
    a GET endpoint to get questions based on category
    '''
    category = Category.query.filter_by(id=c_id).one_or_none()
    
    if (category is None):
        abort(400)

    selection = Question.query.filter_by(category=c_id).all()
    questions = paginate_Questions(request, selection)

    return jsonify({
      'success': True,
      'questions': questions,
      'current_category': c_id,
      'total_questions':len(questions)



    })
    




  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  ##tested
  @app.route('/quizzes', methods=['POST'])
  def random_quiz():
        '''  
        a POST endpoint that takes category and previous question parameters 
        and returns a random question
        '''
        body = request.get_json()
        category = body.get('quiz_category',None)
        previous_questions = body.get('previous_questions',None)

        if (category==None or previous_questions == None):
          abort(400)
        
        if (category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        question = random.choice(questions)

        while (question in previous_questions == True):
            question = get_random_question()

        return jsonify({
            'success': True,
            'question': question.format()
        })

 

  






  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  
  return app

    