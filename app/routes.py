from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddForm, DelForm, ResetPasswordRequestForm, ResetPasswordForm

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, FreeInterval
from app.email import send_password_reset_email

from scripts import intersections as IN
from scripts import timeparsing as TP
#from scripts import ut as UT

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    addform, delform = AddForm(), DelForm()
    # creating/adding intervals using submitted add form data
    if addform.validate_on_submit() and addform.submit.data:
       fi = FreeInterval(author=current_user, 
                         start_day=addform.sd.data, 
                         start_time=addform.st.data, 
                         end_day=addform.ed.data, 
                         end_time=addform.et.data)
       db.session.add(fi)
       db.session.commit()
       flash('Interval added, thanks')
       return redirect(url_for('index'))
    # deleting interval using submitted delete form data
    elif delform.validate_on_submit() and delform.submit.data:
        intervals = FreeInterval.query.all()
        target = filter(lambda x: x.id == delform.interval_id.data, intervals)
        for i in target:
            if i.author == current_user:
                db.session.delete(i)
                flash('Deleting interval')
            else:
                flash("You can't delete someone else's interval.")
        db.session.commit()
        return redirect(url_for('index'))

    schedule = FreeInterval.query.filter_by(author=current_user)
    return render_template('index.html', 
                            title='Home', 
                            addform=addform, 
                            delform=delform, 
                            schedule=schedule)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                    course=form.course.data, 
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # purge schedule
        if form.clear.data:
            s = FreeInterval.query.filter_by(author=current_user)
            for i in s:
                db.session.delete(i)
            flash('Deletion successful!')
        current_user.username = form.username.data
        current_user.course = form.course.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.course.data = current_user.course
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        if form.password.data == "password":
            flash('password? really?')
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/request_partner', methods=['GET', 'POST'])
@login_required
def request_partner():
    compatible_users = filter(lambda x: x.username != current_user.username, 
                              User.query.filter_by(course=current_user.course))
    if not compatible_users:
        flash('sorry, there are no compatible users, please try again later.')
        return redirect(url_for('index'))
    elif len(list(compatible_users)) < 1:
        flash('sorry, there are no compatible users, please try again later.')
        return redirect(url_for('index'))

    my_intervals = map(lambda x: tuple(map(str, [x.start_day, 
                                                 x.start_time, 
                                                 x.end_day, 
                                                 x.end_time])), 
                       current_user.free_times)

    curr_best = (None, None, 0)
    for you in compatible_users:
        your_intervals = map(lambda x: tuple(map(str, [x.start_day, 
                                                       x.start_time, 
                                                       x.end_day, 
                                                       x.end_time])),
                                    you.free_times)
        
        try:
            mins1, mins2      = TP.timestr_to_minutes(my_intervals), TP.timestr_to_minutes(your_intervals)
            tree1, tree2      = IN.list_to_intervaltree(mins1), IN.list_to_intervaltree(mins2)
            intertree         = IN.intervaltree_intersections(tree1, tree2)
            interlist         = IN.condense_intervals(intertree)
            newtree           = IN.intervals_to_tree(interlist)
            intersection_mins = IN.tree_to_list(newtree)
            free_inter_ts     = TP.minutes_to_timestr(intersection_mins)
            combined_ft       = IN.total_free_time(intersection_mins)

            if combined_ft > curr_best[2]:
                curr_best = (you, free_inter_ts, combined_ft)
        except Exception as inst:
            flash(reduce(lambda x, y: x+y, inst.args, 
                         "error(s) in partner requet: ")+".")
            flash('check that your schedule is correctly formatted and try again.')
            return redirect(url_for('index'))
    best_match, overlap, total = curr_best

    if total:
        overlap = map(lambda x: ""+(x[0])+" at "+(x[1])+" until "+(x[2])+" at "+(x[3])+".", overlap )
        return render_template('request_partner.html', 
                                title='Request Partner', 
                                partner=best_match.username, 
                                schedule=overlap, 
                                ft=total,
                                link=str(best_match.username))
    else:
        flash('sorry, we could not find you a match! please try again later.')
        return redirect(url_for('index'))


