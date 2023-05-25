from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for publications whose pub_date
        is in the future
        """
        time = timezone.now() + timedelta(days=30)    # future time

        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is
        older than 1 day
        """
        time = timezone.now() - timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is
        within the last day
        """
        time = timezone.now() - timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create question with the given `question_text` and publish the given number
    of `days` offset to now (negative for questions published in the past,
    positive for questions that have yet to be published)
    """
    time = timezone.now() + timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no question exists, an appropriate message is displayed.
        """
        response = self.client.get(path=reverse(viewname='polls:index'))
        self.assertEqual(first=response.status_code, second=200)
        self.assertContains(response=response, text='No polls are available')
        self.assertQuerySetEqual(
            qs=response.context['latest_question_list'], values=[]
        )

    def test_past_questions(self):
        """
        Questions with a `pub_date` in the past are displayed on the index
        page.
        """
        question = create_question(question_text='Past question', days=-30)
        response = self.client.get(path=reverse(viewname='polls:index'))
        self.assertQuerySetEqual(
            qs=response.context['latest_question_list'], values=[question]
        )

    def test_future_question(self):
        """
        Question with a `pub_date` in the futur aren't displayed on the index
        page
        """
        create_question(question_text='Future question', days=30)
        response = self.client.get(path=reverse(viewname='polls:index'))
        self.assertContains(response=response, text='No polls are available')
        self.assertQuerySetEqual(qs=response.context['latest_question_list'], values=[])

    def test_future_and_past_question(self):
        """
        Even if both future and past questions exist, only past questions are
        displayed
        """
        past_question = create_question(question_text='Past question', days=-30)
        create_question(question_text='Future Question', days=30)
        response = self.client.get(path=reverse(viewname='polls:index'))
        self.assertQuerySetEqual(
            qs=response.context['latest_question_list'], values=[past_question]
        )

    def test_two_past_questions(self):
        """
        Multiple published past questions can be displayed.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The details of a question with `pub_date` in the future returns a 404
        not found.
        """
        future_question = create_question(question_text='Future Question', days=5)
        url = reverse(viewname='polls:detail', args=(future_question.pk,))
        response = self.client.get(path=url)
        self.assertEqual(first=response.status_code, second=404)

    def test_past_question(self):
        """
        The detail view of a `pub_date` in the past displays the question text
        """
        past_question = create_question(question_text='Past Question', days=-1)
        url = reverse(viewname='polls:detail', args=(past_question.pk,))
        response = self.client.get(path=url)
        self.assertContains(response=response, text='Past Question')
