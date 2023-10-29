from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from students.models import Student, Course
from rest_framework.test import APIClient


class CourseTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = baker.make(Student)
        self.course = baker.make(Course, students=(self.student,))
        self.course_list_url = reverse('courses-list')
        self.course_detail_url = reverse('courses-detail', kwargs={'pk': self.course.pk})

    def tearDown(self):
        Course.objects.all().delete()
        Student.objects.all().delete()

    def test_retrieve_course(self):
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.course.id)

    def test_list_courses(self):
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.course.id)

    def test_filter_courses_by_id(self):
        course2 = baker.make(Course)
        filter_url = f"{self.course_list_url}?id={course2.id}"
        response = self.client.get(filter_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], course2.id)

    def test_filter_courses_by_name(self):
        course2 = baker.make(Course, name="Math")
        filter_url = f"{self.course_list_url}?name=Math"
        response = self.client.get(filter_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], course2.name)

    def test_create_course(self):
        data = {
            'name': 'History',
            'students': [self.student.id],
        }
        response = self.client.post(self.course_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(response.data['name'], data['name'])
        self.assertIn(self.student.id, response.data['students'])