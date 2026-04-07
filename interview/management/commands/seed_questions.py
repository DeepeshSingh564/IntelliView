from django.core.management.base import BaseCommand
from interview.models import Role, Question


class Command(BaseCommand):
    help = "Seed the database with sample interview questions"

    def handle(self, *args, **kwargs):
        # Create roles
        roles_data = [
            {"name": "Backend Developer", "slug": "backend-developer", "description": "Backend programming and architecture"},
            {"name": "Data Scientist", "slug": "data-scientist", "description": "Data science, ML, and statistics"},
            {"name": "DevOps Engineer", "slug": "devops-engineer", "description": "CI/CD, cloud, and infrastructure"},
            {"name": "Frontend Developer", "slug": "frontend-developer", "description": "Frontend development and UI/UX"},
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                slug=role_data["slug"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                }
            )
            if created:
                self.stdout.write(f"Created role: {role.name}")

        # Get role objects
        backend_role = Role.objects.get(slug="backend-developer")
        data_role = Role.objects.get(slug="data-scientist")
        devops_role = Role.objects.get(slug="devops-engineer")
        frontend_role = Role.objects.get(slug="frontend-developer")

        # Questions data
        questions_data = {
            backend_role: [
                ("What is the difference between monolithic and microservices architecture?", "medium", ["monolithic", "microservices", "architecture"]),
                ("Explain the role of an API gateway in backend systems.", "hard", ["API Gateway", "routing", "security"]),
                ("What are common HTTP methods and when are they used?", "easy", ["GET", "POST", "PUT", "DELETE"]),
                ("How do you optimize database queries for performance?", "hard", ["indexing", "joins", "query optimization"]),
                ("What is connection pooling and why is it useful?", "medium", ["connection pooling", "database", "performance"]),
                ("Explain REST vs GraphQL APIs.", "medium", ["REST", "GraphQL", "APIs"]),
                ("What strategies do you use for caching in backend systems?", "hard", ["caching", "Redis", "performance"]),
                ("How does authentication differ from authorization?", "easy", ["authentication", "authorization", "security"]),
                ("Explain eventual consistency in distributed systems.", "hard", ["eventual consistency", "distributed systems"]),
                ("What are common backend scalability challenges?", "medium", ["scalability", "load balancing", "bottlenecks"]),
            ],
            data_role: [
                ("What is the difference between supervised and unsupervised learning?", "easy", ["supervised", "unsupervised", "machine learning"]),
                ("Explain overfitting and underfitting in ML models.", "medium", ["overfitting", "underfitting", "bias variance"]),
                ("What are common feature selection techniques?", "hard", ["feature selection", "PCA", "regularization"]),
                ("How do you handle missing data in datasets?", "medium", ["missing data", "imputation", "dropna"]),
                ("Explain precision, recall, and F1-score.", "easy", ["precision", "recall", "F1 score"]),
                ("What is the difference between bagging and boosting?", "medium", ["bagging", "boosting", "ensemble methods"]),
                ("How does gradient descent work?", "easy", ["gradient descent", "optimization", "loss function"]),
                ("What is regularization and why is it important?", "medium", ["regularization", "L1", "L2"]),
                ("Explain the bias-variance tradeoff.", "hard", ["bias", "variance", "tradeoff"]),
                ("How do you evaluate the performance of a clustering algorithm?", "hard", ["clustering", "silhouette score", "evaluation"]),
            ],
            devops_role: [
                ("What is the difference between continuous integration and continuous deployment?", "easy", ["CI", "CD", "DevOps"]),
                ("Explain the concept of Infrastructure as Code (IaC).", "medium", ["Infrastructure as Code", "Terraform", "Ansible"]),
                ("How does Docker differ from virtual machines?", "easy", ["Docker", "containers", "VMs"]),
                ("What are Kubernetes pods and deployments?", "medium", ["Kubernetes", "pods", "deployments"]),
                ("How do you monitor system performance in production?", "hard", ["monitoring", "Prometheus", "Grafana"]),
                ("What is load balancing and why is it important?", "easy", ["load balancing", "HAProxy", "scalability"]),
                ("How do you implement zero-downtime deployments?", "hard", ["zero-downtime", "blue-green deployment", "rolling updates"]),
                ("What are common security practices in DevOps?", "medium", ["DevSecOps", "secrets management", "firewalls"]),
                ("Explain the use of CI/CD pipelines.", "medium", ["pipelines", "Jenkins", "GitHub Actions"]),
                ("How do you handle logging and alerting?", "hard", ["logging", "ELK stack", "alerts"]),
            ],
            frontend_role: [
                ("What is the difference between HTML, CSS, and JavaScript?", "easy", ["HTML", "CSS", "JavaScript"]),
                ("Explain how the virtual DOM works in React.", "medium", ["virtual DOM", "React", "reconciliation"]),
                ("What are React hooks and when would you use them?", "medium", ["hooks", "useState", "useEffect"]),
                ("How do you optimize performance in large React apps?", "hard", ["performance", "memoization", "code splitting"]),
                ("What is responsive design and how do you implement it?", "easy", ["responsive design", "media queries", "CSS"]),
                ("Explain CSS flexbox and grid systems.", "medium", ["flexbox", "grid", "layout"]),
                ("What are common differences between client-side and server-side rendering?", "medium", ["CSR", "SSR", "rendering"]),
                ("How do you handle state management in frontend apps?", "hard", ["state management", "Redux", "Context API"]),
                ("What are web accessibility best practices?", "medium", ["accessibility", "ARIA", "WCAG"]),
                ("Explain the concept of progressive web apps (PWA).", "hard", ["PWA", "offline support", "service workers"]),
            ],
        }

        # Create questions
        for role, questions in questions_data.items():
            for question_text, difficulty, keywords in questions:
                question, created = Question.objects.get_or_create(
                    role=role,
                    text=question_text,
                    defaults={
                        "difficulty": difficulty,
                        "keywords": keywords,
                    }
                )
                if created:
                    self.stdout.write(f"Created question for {role.name}: {question_text[:50]}...")

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with roles and questions!"))
