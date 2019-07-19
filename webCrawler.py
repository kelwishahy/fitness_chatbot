import requests, bs4, threading, time, re


# FUNCTIONALITY
'''
1) Accept an input
2) Match the input to one of the strings in self.topics
3) Navigate to the corresponding webpage
4) Navigate to workouts related to the requested topic
5) Extract exercise names, and navigate to the exercise page
6) Check the exercise level (beginner, intermediate, advanced)
7) Return the exercise if it corresponds to the requested level
8) Construct a workout
9) Return the workout to the caller
'''


class crawler:

    # Class variables
    topics = ['chest', 'shoulders', 'abs', 'back', 'biceps', 'tricep', 'legs']

    # Public methods, use externally
    def __init__(self):
        self.query = None
        self.url = 'https://www.bodybuilding.com/topic/'
        self.exerciseSet = set()
        self.workoutLinks = []

        # Mutex lock
        self.lock = threading.Lock()

    def webSearch(self, query):
        # Match the given query to one of the available topics
        query = query.lower()
        if query in self.topics:
            self.query = query

        # Navigate to the requested topic page on www.bodybuilding.com
        self.url = self.url + self.query

        # Download the webpage for html parsing
        res = requests.get(self.url)
        res.raise_for_status()

        page = bs4.BeautifulSoup(res.text, features="html.parser")
        linkContainer = page.find("div", class_="cms-article-list--container")
        articles = linkContainer.find_all('span', class_='cms-article-list--article col col-1')

        threads = []
        for article in articles:
            t = threading.Thread(target=self.getArticles, args=(article,))
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        threads = []
        for i in range(len(self.workoutLinks)):
            t = threading.Thread(target=self.findExercises, args=(self.workoutLinks[i],))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        exerciseSet = set()

        for x in self.exerciseSet:
            exerciseSet.add(x)

        #Reset
        self.url = 'https://www.bodybuilding.com/topic/'
        self.exerciseSet.clear()
        self.workoutLinks.clear()

        return exerciseSet

    def whatIs(self, query):
        self.query = query.lower().replace("-", " ")
        exerciseLink = self.match_query(query)

        res = requests.get(exerciseLink)
        res.raise_for_status()

        page = bs4.BeautifulSoup(res.text, features="html.parser")
        title = page.find('h2', class_='ExHeading ExHeading--h2 ExDetail-h2').text
        video = page.find(class_='ExVideo js-ex-video')['data-src']
        photo = page.find('img', class_='ExImg ExDetail-img js-ex-enlarge')['data-large-photo']

        result = [exerciseLink, photo, video, title]

        return result
    # --------------------------------------------------------------------------

    # Class methods, do not use externally
    def match_query(self, query):
        query = query.lower()
        query = query.replace(" ", "+")
        searchURL = 'https://www.bodybuilding.com/exercises/search?query=' + query
        searchResult = requests.get(searchURL)
        searchResult.raise_for_status()
        searchResult = bs4.BeautifulSoup(searchResult.text, features="html.parser")
        exercises = searchResult.find_all(class_="ExResult-row flexo-container flexo-between")

        for x in exercises:
            title = x.find(class_='ExHeading ExResult-resultsHeading').find('a').text
            u_title = title.lower()
            u_title = u_title.replace("-", " ")
            match = re.search(query.replace("+", " "), u_title)
            if match != None:
                print(match.group(0))
                exercisePath = x.find(class_="ExResult-cell ExResult-cell--nameEtc").find('a')['href']
                url = 'https://www.bodybuilding.com' + exercisePath
                print(url)
                return url

            return None

    def findExercises(self, link):
        # Download the page
        res = requests.get(link)
        res.raise_for_status()

        try:
            page = bs4.BeautifulSoup(res.text, features="html.parser")
            exerciseContainer = page.find('div', class_='cms-article-list__container cms-article__workout-plan bbcomWorkoutPlan')
            exerciseContainer = exerciseContainer.find('div', class_='cms-article-list__content--wrapper')
            exerciseContainer = exerciseContainer.find_all('div', class_='cms-article-list__content--container')

            for ex in exerciseContainer:
                exercise = ex.find('div', class_='cms-article-list__content').find('div')
                exercise = exercise.find('div', class_='cms-article-workout__exercise--info').find('a').text

                while self.lock.acquire() == False:
                    time.sleep(0)

                self.exerciseSet.add(exercise)

                self.lock.release()
        except:
            pass

    def getArticles(self, article):
        articleType = article.find('figure').find('figcaption').find('span', class_='category').text

        if (articleType == 'Workouts'):
            while self.lock.acquire() == False:
                time.sleep(0) # Yield thread

            self.workoutLinks.append(article.find('figure').find('a')['href'])
            self.lock.release()
