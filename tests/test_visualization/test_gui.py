import unittest

from hospital_team1.visualization import create_app


class TestDashboardApp(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def test_dashboard_route_renders(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Hospital Triage Scheduler", body)
        self.assertIn("Waiting Room (候诊区)", body)
        self.assertIn("Project Structure (项目结构参考)", body)


if __name__ == "__main__":
    unittest.main()
