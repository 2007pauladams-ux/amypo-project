from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from news.models import NewsCategory

class AccountsAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name='Frontier Tech',
            slug='frontier-tech',
            icon='cpu',
            badge_class='badge-purple'
        )
        self.user = User.objects.create_user(
            username='analyst_test',
            email='analyst@test.intel',
            password='Password123!',
            first_name='Test',
            last_name='Analyst'
        )

    def test_user_profile_signal_creation(self):
        """Test that UserProfile is automatically created via post_save signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        self.assertEqual(self.user.profile.avatar_color, '#8b5cf6')

    def test_login_successful(self):
        """Test successful authentication and session creation."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'analyst_test',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_invalid_credentials(self):
        """Test failed authentication with wrong credentials."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'analyst_test',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid analyst credentials')

    def test_registration_flow(self):
        """Test analyst profile registration flow."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_analyst',
            'email': 'new@test.intel',
            'first_name': 'New',
            'last_name': 'Cadet',
            'password': 'StrongPassword2026!',
            'confirm_password': 'StrongPassword2026!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_analyst').exists())

    def test_registration_password_mismatch(self):
        """Test registration rejection when passwords do not match."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mismatch_analyst',
            'email': 'mismatch@test.intel',
            'password': 'StrongPassword2026!',
            'confirm_password': 'DifferentPassword2026!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')

    def test_logout_view(self):
        """Test logging out an authenticated session."""
        self.client.login(username='analyst_test', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_update_view(self):
        """Test updating analyst profile and preferred categories."""
        self.client.login(username='analyst_test', password='Password123!')
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@test.intel',
            'bio': 'Frontier quantum analyst tracking superconductors.',
            'categories': [self.category.id],
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.profile.bio, 'Frontier quantum analyst tracking superconductors.')
        self.assertIn(self.category, self.user.profile.preferred_categories.all())
