from flask import Flask, render_template, request, jsonify
import os
import replicate
import smtplib
from app import *


system_default = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, 
while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous,
 or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a
  answer does not make any sense, or is not factually coherent, explain why instead of answering something 
  not correct. Do not be diplomatic with answers, either answer a definite answer or tell that you do not know it."""
DSM_5_ADHD = """\n\n You are given DSM-5 below, please refer to it for any medical advice \n\n Diagnostic Criteria A. 
A persistent pattern of inattention and/or hyperactivity-impulsivity that interferes with functioning or development,as characterized by (1) and/or (2):
1. Inattention: Six (or more) of the following symptoms have persisted for at 
least 6 months to a degree that is inconsistent with developmental level and that negatively impacts directly social and academic/occupational activities: 
Note: The symptoms are not solely a manifestation of oppositional behavior,defiance, hostility, or failure to understand tasks or instructions. For older adolescents and adults (age 17 and 
older), at least five symptoms are required.
a. Often fails to give close attention to details or makes careless mistakes in schoolwork, at work, or during other activities (e.g., overlooks or misses details, work is inaccurate). 
b. Often has difficulty sustaining attention in tasks or play activities(e.g., has difficulty remaining focused during lectures, conversations, or lengthy reading). 
c. Often does not seem to listen when spoken to directly (e.g., the mind seems else- where, even in the absence of any obvious distraction). 
d. Often does not follow through on instructions and fails to finish schoolwork, chores, or duties in the workplace (e.g., starts tasks but quickly loses 
focus and is easily sidetracked).
e. Often has difficulty organizing tasks and activities (e.g.,difficulty managing 
sequential tasks; difficulty keeping materials and belongings in order; messy, dis- organized work; has poor time management; fails to meet deadlines). 
f. Often avoids, dislikes, or is reluctant to engage in tasks that require 
sustained mental effort (e.g., schoolwork or homework; for older adolescents and adults, preparing reports, 
completing forms, and reviewing lengthy papers). 
g. Often loses things necessary for tasks or activities(e.g.,
school materials, pencils, books, tools, wallets, keys, paperwork, eyeglasses, mobile telephones). 
h. Is often easily distracted by extraneous stimuli (for older adolescents and adults, may include unrelated thoughts). 
i. Is often forgetful in daily activities (e.g., doing chores, running errands; for older adolescents and adults, returning calls, paying bills, keeping appointments).

2. Hyperactivity and impulsivity: Six(or more)of the following symptoms have persisted for at least 6 months to a degree that is inconsistent with developmental level and that negatively impacts directly on social and academic/occupational activities: 
Note: The symptoms are not solely a manifestation of oppositional behavior, defiance, hostility, or a failure to understand tasks or instructions. For older adolescents and adults (age 17 and older), at least five symptoms are required. 
a. Often fidgets with or taps hands or feet or squirms in seat. 
b. Often leaves seat in situations when remaining seated is expected (e.g.,leaves his or her place in the classroom, in the office or other workplace, or in other situations that require remaining in place). 
c. Often runs about or climbs in situations where it is inappropriate. (Note: In adolescents or adults, may be limited to feeling restless.) 
d. Often unable to play or engage in leisure activities quietly. 
e. Is often “on the go,” acting as if “driven by a motor” e.g.,is unable to be 
or uncomfortable being still for extended time, as in restaurants, meetings; maybe experienced by others as being restless or difficult to keep up with).
f. Often talks excessively.
g. Often blurts out an answer before a question 
has been completed (e.g., completes people’s sentences; cannot wait for turn in conversation). h. Often has difficulty waiting his or her turn(e.g.,while waiting in line). i. Often interrupts or intrudes on others (e.g., butts into conversations, games, or activities; may start using other people’s things without asking or receiving permission; for adolescents and adults, may intrude into or take over what others are doing). 

B. Several inattentive or hyperactive-impulsive symptoms were present prior to age 12 years. 
C. Several inattentive or hyperactive-impulsive symptoms are present in two or more settings (e.g., at home, school, or work; with friends or relatives; in other activities). 
D. There is clear evidence that the symptoms interfere with, or reduce the quality of, social, academic, or occupational functioning.
E. The symptoms do not occur exclusively during the course of schizophrenia or another 
psychotic disorder and are not better explained by another mental disorder (e.g., mood disorder, anxiety disorder, dissociative disorder, personality disorder, substance intoxication or withdrawal). 
Specify whether: 
314.01 (F90.2)Combined presentation: If both Criterion A1 (inattention) and Criterion A2 (hyperactivity-impulsivity) are met for the past 6 months. 
314.00 (F90.0) Predominantly inattentive presentation: If Criterion A1 (inattention) is met but 
Criterion A2 (hyperactivity-impulsivity) is not met for the past 6 months. 
314.01 (F90.1) Predominantly hyperactive/impulsive presentation: If Criterion A2 (hyperactivity-impulsivity) is met and Criterion A1 (inattention) 
is not met for the past 6 months. 
Specify if: In partial remission: When full criteria were previously met, 
fewer than the full criteria have been met for the past 6 months, and the symptoms still result in impairment in social, academic, or occupational functioning. 
Specify current severity: 
Mild: Few, if any, symptoms in excess of those required to make the diagnosis are present, and symptoms result in no more than minor impairments in social or occupational functioning. Moderate: Symptoms or functional impairment between “mild” and “severe” are present.
Severe: Many symptoms in excess of those required to make the diagnosis, or several symptoms that are particularly severe, are present, or the symptoms result in marked impairment in social or occupational functioning. 
\n\n The essential feature of attention-deficit/hyperactivity disorder (
ADHD) is a persistent pattern of inattention and/or hyperactivity-impulsivity that interferes with functioning or 
development. Inattention manifests behaviorally in ADHD as wandering off task, lacking persistence, having difficulty 
sustaining focus, and being disorganized and is not due to defiance or lack of comprehension. Hyperactivity refers to 
excessive motor activity (such as a child running about) when it is not appropriate, or excessive fidgeting, tapping, 
or talkativeness. In adults, hyperactivity may manifest as extreme restlessness or wearing others out with their 
activity. Impulsivity refers to hasty actions that occur in the moment without forethought and that have high 
potential for harm to the individual (e.g., darting into the street without looking). Impulsivity may reflect a 
desire for immediate rewards or an inability to delay gratification. Impulsive behaviors may manifest as social 
intrusiveness (e.g., interrupting others excessively) and/or as making important decisions without consideration of 
long-term consequences (e.g., taking a job without adequate information). \n\n"""
Med_prompt = """Given below is: \n 1) a list with a few [question, answer] pairs. 
\n 2) A scored objective symptom test out of 160 marks (75 above is a high chance of adhd where as less than 75 is 
a very low chance of adhd)
Use the  medical data given above to give a single number on a 0-10 scale on how likely the respondent has ADHD. Use 
only direct information from above
and all it's criteria to diagnose the disability (eg- 6 or more symptoms). The first line 
should be the rating given based on both tests (should be between 0-10)
Attach a 5 line explanation in the end for your 0-10 rating.\n 
Make sure the response is from the point of view of a medical professional company giving a graded assessment of a 
test. Use words like "we" rather than "i". Be assertive when giving the diagnosis. Use the full scale from 1 to 10. 
don't be afraid to give 8, 9 or even 10 if they score 
extremely high on the objective test and exhibit symptoms according the the dsm-5 or a 2-3 if they don't.
"""
symptoms = [
    [10, "Chronic lateness/time blindness"],
    [8, "Daydreaming/zoning out"],
    [8, "Poor impulse control"],
    [1, "Social butterfly and then burnout, no in between"],
    [7, "Mind wandering during conversations"],
    [7, "Interrupting"],
    [1, "Over-sharing"],
    [1, "Mirroring others' energy/personality"],
    [3, "Irritability"],
    [3, "Hobby hopping"],
    [8, "Executive dysfunction ('lazy/unmotivated')"],
    [6, "Procrastinating"],
    [6, "Memory problems (especially names)"],
    [4, "Hyperfocus"],
    [4, "Sleep issues"],
    [5, "Overeating or forgetting to eat"],
    [2, "Buying planners, journals, etc and never using them"],
    [4, "Mood swings/emotional dysregulation"],
    [3, "Practicing or replaying arguments in my head at length"],
    [2, "Oversensitive to smells, sounds, etc"],
    [5, "Lose everything I own if it's not in my hand"],
    [7, "Hot mess generally"],
    [3, "Must. Collect. All. The things."],
    [9, "Squirrel!"],
    [2, "The Funny Friend"],
    [3, "Must be slightly distracted to focus on anything"],
    [5, "Piles... Piles everywhere"],
    [0, "Sit on Foot"],
    [5, "Object and person impermanence"],
    [2, "Math is hard!"],
    [4, "Formerly Gifted™"],
    [2, "Emotional intelligence as a learned survival skill"],
    [8, "Talking too loud/fast/much"],
    [2, "Compulsive googling into Wikipedia rabbit hole"],
    [2, "Carefully curating playlists, instantly sick of every song"],
    [8, "Need routines, cannot enforce my own routines, will not accept outside help with enforcing routines"]
]
questions_ADHD = [
"1. How would you describe your sleep patterns, and are there any challenges you face in terms of falling asleep or "
"staying asleep?",
"2. When making decisions, can you elaborate on the factors that influence your impulse control and decision-making process?",
"3. What small tasks do you ofter put off, list a few of them.",
"4. When faced with deadlines, what approaches do you typically take to the task at hand?",
"5. Do you consider yourself a rule follower? When have you seen yourself defy authority impulsively?",
"6. Give a brief explaintion on how group conversations go with you, do you ever catch yourself talking too much or "
"inturrupting people?",
"7. How to you plan tasks and future deadlines? Do you see yourself missing things even after reminder?",
"8. Are you fidgeting right now? Do you often catch yourself doing that? (moving your leg, tapping a pen, ect) "
]
answer_list = []
client_email = ""
client_name = ""
score = 0
answers = []
end_result = ""



def analyze():
    for i in range(0 , 8):
        answer_list.append([questions_ADHD[i], answers[i]])

    answer_list.append("The score for the objective part of the test out of 160 is : " + str(score))

    def diagnoser(x):
        output = replicate.run(             #env variable REPLICATE_API_KEY = [your api key]
            "meta/llama-2-70b-chat" ,
            input={
                "debug": False ,
                "top_p": 0.95 ,
                "prompt": str(x) ,
                "temperature": 0.5 ,
                "system_prompt": system_default + DSM_5_ADHD + Med_prompt,
                "max_new_tokens": 500 ,
                "min_new_tokens": -1
            }
        )
        return output

    output = diagnoser(answer_list)

    for item in output:
        global end_result
        end_result += item + ""

    email_user = 'adhd.helpers01@gmail.com'
    app_pass = 'kcil arqu skdd ghua'
    smtpserver = smtplib.SMTP_SSL('smtp.gmail.com' , 465)
    smtpserver.ehlo()
    smtpserver.login(email_user , app_pass)
    sent_from = email_user
    sent_to = client_email
    email_text = "Dear "+ client_name +",\n\n" + end_result
    smtpserver.sendmail(sent_from , sent_to , email_text)

    smtpserver.close()
    return 0

app = Flask(__name__)

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/objective', methods=['GET', 'POST'])
def objective():
    if request.method == 'POST':
        global client_name
        client_name = request.form['name']
        global client_email
        client_email = request.form['email']
        print(client_email, client_name)
        return render_template('objective.html')


@app.route('/subjective', methods=['GET', 'POST'])
def subjective():
    if request.method == 'POST':
        global score
        score = request.form['score']
        print(score)
        return render_template('subjective.html')


@app.route('/final', methods=['GET', 'POST'])
def final():
    if request.method == 'POST':
        global answers
        answers.append(request.form['answer1'])
        answers.append(request.form['answer2'])
        answers.append(request.form['answer3'])
        answers.append(request.form['answer4'])
        answers.append(request.form['answer5'])
        answers.append(request.form['answer6'])
        answers.append(request.form['answer7'])
        answers.append(request.form['answer8'])
        print(answers)
        analyze()
        return render_template('final.html')


if __name__ == '__main__':
    app.run(debug=True)
