#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/6/8 23:27
# @Author  : YOURNAME
# @FileName: app.py
# @Software: PyCharm
from flask import Flask, render_template
from flask import url_for
from flask import request
from flask import redirect
from flask import flash
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

name = 'neuron'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

"""
导入包
实例化flask对象 app
"""


@app.cli.command()
@click.option('--drop', is_flag=True, help='create after drop.')
def initdb(drop):
    """Initialize the database"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 注册函数，绑定一个url
@app.route('/', methods=['GET', 'POST'])
def index():
    # movies = Movie.query.all()
    # return 'Welcome to My WatchList<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'
    # return render_template('index.html', name=name, movies=movies)
    if request.method == 'POST': #判断是否为POST请求
        #获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or year or len(year) >4 or len(title) >60 :
            flash('Invalid Input')
            return redirect(url_for('index'))
        #保存表单数据
        movie = Movie(title=title, year= year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created')
        return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/home')
def hello():
    return '<h1>Hello Totoro!</h1><img src="https://helloflask.com/totoro.gif">'


@app.route('/usr/<name>')
def user_page(name):
    return f'USer:{escape(name)}'


@app.route('/test')
def test_usr_for():
    print(url_for('hello'))
    print(url_for('user_page', name='neuron'))
    print(url_for('test_usr_for'))
    print(url_for('test_usr_for', name=2))
    return 'Test page'


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    user = User.query.first()
    print(user)
    return render_template('404.html', user=user), 404


@app.context_processor
def inject_user():  # 函数名字可以随意更改
    user = User.query.first()
    return dict(user=user)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):

    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form('title')
        year = request.form('year')
        if not title or year or len(year) >4 or len(title) >60 :
            flash('Invalid Input')
            return redirect(url_for('index'))
        #保存表单数据
        movie.title = title
        movie.year = year

        db.session.commit()
        flash('Item created')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)



@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

